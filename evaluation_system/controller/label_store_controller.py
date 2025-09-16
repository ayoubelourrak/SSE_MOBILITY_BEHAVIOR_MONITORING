import os
import sqlite3
import sys
import datetime

from model.system_configuration import SystemConfiguration


class LabelStore:
    _instance = None

    def __init__(self):
        self._configuration = SystemConfiguration()
        self._db_name = self._configuration.db_name
        # Create data directory if it doesn't exist
        data_dir = os.path.join(os.path.abspath('.'), 'data')
        os.makedirs(data_dir, exist_ok=True)

        db_path = os.path.join(data_dir, self._db_name)
        if os.path.exists(db_path):
            print('[+] sqlite3 previous database deleted')
            os.remove(db_path)

        if self.open_connection() and self.create_table():
            print('[+] sqlite3 connection established and raw_session table initialized')
            pass
        else:
            print('sqlite3 initialize failed')
            sys.exit(1)

    @staticmethod
    def get_instance():
        if LabelStore._instance is None:
            LabelStore._instance = LabelStore()
        return LabelStore._instance

    def open_connection(self) -> bool:
        """
        Creates the connection to the database
        :return: True if the connection is successful. False if the connection fails.
        """
        try:
            data_dir = os.path.join(os.path.abspath('.'), 'data')
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, self._db_name)
            self.conn = sqlite3.connect(db_path)
            return True
        except sqlite3.Error as e:
            print(f"[ERROR] sqlite3 open connection error {e}")

        return False

    def check_connection(self) -> None:
        """
        Checks if the connection with the database is established.
        It terminates the system if the connection is not set.
        """
        if self.conn is None:
            print('[ERROR] sqlite3 connection not established')
            sys.exit(1)

    def store_label(self, label) -> bool:
        """
        stores the label in the database the table to look for is the one in label["label_source"]
        :param label: dict with keys 'uuid', 'label', 'label_source'
        :return: True if the label is stored successfully.
        """
        self.check_connection()

        # Validate label_source
        if label["label_source"] not in ['production', 'ingestion']:
            print(f"[ERROR] Invalid label_source: {label['label_source']}. Must be 'production' or 'ingestion'")
            return False

        try:
            table_name = label["label_source"]
            # Add timestamp when storing the label
            timestamp = datetime.datetime.now().isoformat()

            query = f'''INSERT OR REPLACE INTO {table_name}
                       (uuid, label, label_source, timestamp)
                       VALUES (?, ?, ?, ?)'''

            cursor = self.conn.cursor()
            cursor.execute(query, (label["uuid"], label["label"], label["label_source"], timestamp))
            self.conn.commit()

            print(f"[+] Label stored in {table_name} table: UUID={label['uuid']} at {timestamp}")
            return True

        except sqlite3.Error as e:
            print(f"[ERROR] sqlite3 store_label error {e}")
            return False

    def create_table(self) -> bool:
        """
        :return: True if the creation is successful. False otherwise.
        """
        self.check_connection()

        try:
            query1 = ('CREATE TABLE IF NOT EXISTS ingestion ('
                      'uuid text, '
                      'label text, '
                      'label_source text, '
                      'timestamp text, '
                      'UNIQUE(uuid), PRIMARY KEY(uuid))')
            query2 = ('CREATE TABLE IF NOT EXISTS production ('
                      'uuid text, '
                      'label text, '
                      'label_source text, '
                      'timestamp text, '
                      'UNIQUE(uuid), PRIMARY KEY(uuid))')

            cursor = self.conn.cursor()
            cursor.execute(query1)
            cursor.execute(query2)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"[ERROR] sqlite3 create_tables error {e}")
            return False

        return True

    def label_pairs_number(self) -> int:
        """
        return the number of labels uuid that have a row in both the database tables
        :return: number of UUID pairs that exist in both tables
        """
        self.check_connection()

        try:
            query = '''SELECT COUNT(*)
                       FROM ingestion i
                                INNER JOIN production p ON i.uuid = p.uuid'''

            cursor = self.conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()

            count = result[0] if result else 0
            print(f"[+] Found {count} label pairs")
            return count

        except sqlite3.Error as e:
            print(f"[ERROR] sqlite3 label_pairs_number error {e}")
            return 0


    def remove_labels(self, labels_ids) -> bool:
        """
        removes the labels from the database
        :param labels_ids: list of labels uuids to remove
        :return: True if all labels were removed successfully
        """
        self.check_connection()

        if not labels_ids:
            print("[WARNING] No label IDs provided for removal")
            return True

        try:
            cursor = self.conn.cursor()
            success = True

            for uuid in labels_ids:
                # Remove from ingestion table
                query_ingestion = "DELETE FROM ingestion WHERE uuid = ?"
                cursor.execute(query_ingestion, (uuid,))
                ingestion_removed = cursor.rowcount

                # Remove from production table
                query_production = "DELETE FROM production WHERE uuid = ?"
                cursor.execute(query_production, (uuid,))
                production_removed = cursor.rowcount

                total_removed = ingestion_removed + production_removed
                if total_removed > 0:
                    print(f"[+] Removed label UUID={uuid} from {total_removed} table(s)")
                else:
                    print(f"[WARNING] Label UUID={uuid} not found in any table")

            self.conn.commit()
            return success

        except sqlite3.Error as e:
            print(f"[ERROR] sqlite3 remove_labels error {e}")
            return False

    def get_label_pairs(self) -> list:
        """
        get a list of labels in the format {'uuid', 'label_ingestion', 'label_production'}
        ordered by when they arrived from the production system
        :return: list of dictionaries containing label pairs
        """
        self.check_connection()

        try:
            query = '''SELECT i.uuid, i.label as label_ingestion, p.label as label_production, p.timestamp as production_timestamp
                       FROM ingestion i
                       INNER JOIN production p ON i.uuid = p.uuid
                       ORDER BY p.timestamp ASC'''

            cursor = self.conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()

            label_pairs = []
            for row in results:
                label_pair = {
                    'uuid': row[0],
                    'label_ingestion': row[1],
                    'label_production': row[2],
                    'production_timestamp': row[3]
                }
                label_pairs.append(label_pair)

            print(f"[+] Retrieved {len(label_pairs)} label pairs (ordered by production timestamp)")
            return label_pairs

        except sqlite3.Error as e:
            print(f"[ERROR] sqlite3 get_label_pairs error {e}")
            return []

    def close_connection(self):
        """
        Closes the database connection
        """
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            print('[+] sqlite3 connection closed')

    def __del__(self):
        """
        Destructor to ensure connection is closed
        """
        self.close_connection()