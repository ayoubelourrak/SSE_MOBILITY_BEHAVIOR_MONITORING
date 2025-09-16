import os
import sys
import logging
import time
from threading import Thread
from jsonschema import ValidationError
from src.raw_session_integrity import RawSessionIntegrity
from src.raw_sessions_store import RawSessionsStore
from src.ingestion_system_configuration import IngestionSystemConfiguration
from src.json_io import JsonIO

CONFIG_PATH = './data/ingestion_system_config.json'
CONFIG_SCHEMA_PATH = './data/ingestion_system_config_schema.json'

'''
Module Name: IngestionSystem
Description: This class acts as a controller for the system.
'''

class IngestionSystem:
    """
    This class acts as a controller for the system
    """

    def __init__(self) -> None:
        """
        Initializes the system
        """
        try:
            self.configuration = IngestionSystemConfiguration(CONFIG_PATH, CONFIG_SCHEMA_PATH)
        except ValidationError:
            logging.error('Error during the Ingestion System initialization phase')
            sys.exit(1)
        self.last_uuid_received = None
        self.evaluation = bool(int(os.getenv('EVALUATION')))
        self.sessions_to_evaluation = 0
        self.sessions_to_produce = 0
        self.operative_mode = self.configuration.operative_mode
        print(f'[+] The configuration is valid, {self.operative_mode} mode')

    def run(self) -> None:
        """
        Runs the Ingestion System main process
        """
        # TODO i log.info non funzionano metti i print
        print(f'[+] The configuration is valid, {self.operative_mode} mode')

        # Create an instance of RawSessionsStore
        raw_sessions_store = RawSessionsStore()
        # Create an instance of RawSessionIntegrity
        raw_session_integrity = RawSessionIntegrity()
        # Run REST server
        listener = Thread(target=JsonIO.get_instance().listen, args=('0.0.0.0', 4000), daemon=True)
        listener.start()
        #while JsonIO.get_instance().receive() is False:
        #    time.sleep(3)
        while True:
            # Wait for a new record
            received_record = JsonIO.get_instance().receive()
            print('received record: {}'.format(received_record))

            last_missing_sample = False
            if raw_sessions_store.store_record(record=received_record):
                if self.last_uuid_received is not None:
                    if self.last_uuid_received == received_record['uuid']:
                        # Check on the current session
                        session_complete = raw_sessions_store. \
                        is_session_complete(uuid=received_record['uuid'], \
                                            last_missing_sample=False, \
                                            evaluation=self.evaluation)
                        uuid = received_record['uuid']
                    else:
                        # Check on the previous session because of a missing sample
                        print(f'Raw Session {self.last_uuid_received} missing sample detected')
                        session_complete = raw_sessions_store. \
                                            is_session_complete(uuid=self.last_uuid_received, \
                                                                last_missing_sample=True, \
                                                                evaluation=self.evaluation)
                        uuid = self.last_uuid_received
                        self.last_uuid_received = received_record['uuid']
                        last_missing_sample = True

                    if session_complete:
                        # If the session is complete there is no need for the next record to test"
                        self.last_uuid_received = None
                        print(f'Raw Session {uuid} complete')

                        # Load Raw Session from the Data Store
                        raw_session = raw_sessions_store.load_raw_session(uuid=uuid)

                        if raw_session['uuid'] is None:
                            print(f'Raw Session {self.last_uuid_received} failed to be loaded')
                            continue

                        # Delete Raw Session from the Data Store
                        raw_sessions_store.delete_raw_session(uuid=uuid)

                        # Check Raw Session integrity
                        good_session = raw_session_integrity. \
                        mark_missing_samples(time_series=raw_session['time_series'])

                        if good_session:
                            # Send Raw Session to the Preparation System
                            sent_to_preparation = JsonIO.get_instance(). \
                                                send(data=raw_session, \
                                                dest_system="preparation")

                            if sent_to_preparation:
                                print(f'Raw Session {uuid} sent to the Preparation System')

                            if self.evaluation:
                                # Send Raw Session to the Evaluation System
                                label = {'uuid': raw_session['uuid'], \
                                        'label': raw_session['pressure_detected']}
                                sent_to_evaluation = JsonIO.get_instance(). \
                                                        send( data=label, \
                                                            dest_system="evaluation")
                                if sent_to_evaluation:
                                    print(f'Label {raw_session["pressure_detected"]} sent to the evaluation System')
                                    self.sessions_to_evaluation += 1
                                    print(f'Labels to sent to the evaluation System: {self.sessions_to_evaluation}')
                                    if self.sessions_to_evaluation == self.configuration.evaluation_window:
                                        self.sessions_to_evaluation = 0
                                        self.evaluation = False
                                        print('Evaluation phase ended')
                            else:
                                if self.operative_mode == 'production':
                                    self.sessions_to_produce += 1
                                    print(f'Sessions executed: {self.sessions_to_produce}')

                                    # TODO sistema le dimensioni del window
                                    if self.sessions_to_produce == self.configuration.production_window:
                                        self.evaluation = True
                                        self.sessions_to_produce = 0
                                        logging.info('Entering in evaluation phase')
                                        print('Entering in evaluation phase')
                        else:
                            logging.error('Raw Session %s discarded, threshold not satisfied', \
                                         uuid)
                    else:
                        if last_missing_sample:
                            logging.error('Raw Session %s not complete [no recovery possible]', \
                                          uuid)
                            # Session not complete (meaning that some required record is missing)
                            # The system will not receive any other record
                            # related to this session (lost) so it must be delete from the store
                            raw_sessions_store.delete_raw_session(uuid=uuid)
                            self.last_uuid_received = None
                else:
                    self.last_uuid_received = received_record['uuid']
