import os
import sqlite3
import sys
import threading
import queue
import time
from datetime import datetime

DATABASE_NAME = "records.db"

class RecordTimestampManager:

    def __init__(self):
        db_path = os.path.join(os.path.abspath('.'), 'logs', DATABASE_NAME)

        # Delete database if it exists
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"Deleted existing database: {db_path}")

        # Ensure logs directory exists
        logs_dir = os.path.dirname(db_path)
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        self.db_path = db_path

        # Initialize queue for log processing
        self.log_queue = queue.Queue()

        # Create database and table before starting worker thread
        temp_conn = sqlite3.connect(db_path)
        temp_cursor = temp_conn.cursor()
        temp_cursor.execute('''
                            CREATE TABLE IF NOT EXISTS record_timestamps
                            (
                                record_id
                                TEXT
                                PRIMARY
                                KEY
                            )
                            ''')
        temp_conn.commit()
        temp_conn.close()

        # Small delay to ensure database is created
        time.sleep(0.1)

        # Start worker thread after database initialization
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()


    def _process_queue(self):
        """Worker thread that processes log entries from the queue."""
        # Create database connection for this worker thread with retry logic
        connection = None
        cursor = None
        max_retries = 5

        for attempt in range(max_retries):
            try:
                # Wait a bit longer if this is a retry
                if attempt > 0:
                    time.sleep(0.5 * attempt)

                connection = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30.0)
                connection.execute("PRAGMA journal_mode=WAL")
                connection.execute("PRAGMA synchronous=NORMAL")
                connection.execute("PRAGMA cache_size=10000")
                connection.execute("PRAGMA temp_store=MEMORY")
                connection.execute("PRAGMA busy_timeout=30000")
                cursor = connection.cursor()
                break
            except sqlite3.Error as e:
                print(f'[-] Worker Thread Sqlite Connection Error [{e}] - Attempt {attempt + 1}/{max_retries}')
                if connection:
                    connection.close()
                if attempt == max_retries - 1:
                    print(f'[-] Failed to connect to database after {max_retries} attempts')
                    return

        while True:
            try:
                # Block and wait for log entry from queue
                log_entry = self.log_queue.get(block=True)

                # Process the log entry
                self._add_timestamp_direct(log_entry['record_id'], log_entry['system_source'], log_entry['timestamp'], connection, cursor)

                # Mark task as done
                self.log_queue.task_done()

            except Exception as e:
                print(f"Error processing log entry: {e}")
                # Mark task as done even if there was an error
                try:
                    self.log_queue.task_done()
                except ValueError:
                    pass

    def _add_timestamp_direct(self, record_id: str, system_source: str, timestamp: datetime = None, connection=None, cursor=None):
        """Direct database operation - used by worker thread."""
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        try:
            # Check if the column for the system_source exists
            try:
                cursor.execute(f"ALTER TABLE record_timestamps ADD COLUMN {system_source} TEXT")
            except sqlite3.OperationalError:
                # Column already exists
                pass

            if record_id.lower() == 'all':
                cursor.execute(f"UPDATE record_timestamps SET {system_source} = ?", (timestamp,))
            else:
                # Check if the record_id exists, if not, insert it
                cursor.execute("INSERT OR IGNORE INTO record_timestamps (record_id) VALUES (?)", (record_id,))

                # Update the timestamp
                cursor.execute(f"UPDATE record_timestamps SET {system_source} = ? WHERE record_id = ?",
                                     (timestamp, record_id))

            connection.commit()
        except Exception as e:
            print(f"Database error: {e}")

    def add_timestamp(self, record_id: str, system_source: str, timestamp: datetime = None):
        """Public method that adds log entries to the queue for processing."""
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        log_entry = {
            'record_id': record_id,
            'system_source': system_source,
            'timestamp': timestamp
        }

        # Add to queue for processing
        self.log_queue.put(log_entry)

    def close(self):
        """Closes the queue and waits for pending operations."""
        # Wait for all queued items to be processed
        self.log_queue.join()
