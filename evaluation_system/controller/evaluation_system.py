import sys
from threading import Thread
from jsonschema import ValidationError
from controller.label_store_controller import LabelStore
from controller.report_controller import ReportController
from model.json_validator import JsonValidator
from model.msg_manager import MessageManager
from model.system_configuration import SystemConfiguration


class EvaluationSystem:

    def __init__(self):
        print("[INFO] Initializing Evaluation System")
        try:
            JsonValidator.validate_schemas()
        except ValidationError as e:
            print("[ERROR] Impossible to validate configuration file, exit")
            print(f"[ERROR] {e}")
            sys.exit(1)
        self._configuration = SystemConfiguration()
        print("[INFO] Configuration Done")
        print("[INFO] Store Configuration Done")
        self.report_controller = ReportController()

    def run(self):
        print("[INFO] Starting Evaluation System...")

        # Start Flask server in a separate thread
        run_thread = Thread(target=MessageManager.get_instance().start_server, daemon=True)
        run_thread.start()
        print("[INFO] Flask server started")

        print("[INFO] Waiting for labels...")

        while True:
            try:
                # Get message from queue (blocking)
                message = MessageManager.get_instance().get_queue().get(block=True)

                # Skip start messages
                if isinstance(message, bool):
                    print("[INFO] Received start signal")
                    continue

                # Store the label (message is already a Label object)
                label_data = message.to_json()
                success = LabelStore.get_instance().store_label(label_data)

                if not success:
                    print(f"[WARNING] Failed to store label: {label_data}")
                    continue

                # Check if we have enough label pairs to generate a report
                pair_count = LabelStore.get_instance().label_pairs_number()
                print(f"[INFO] Current label pairs: {pair_count}/{self._configuration.report_size}")

                if pair_count >= self._configuration.report_size:
                    print("[INFO] Sufficient label pairs collected. Generating report...")
                    labels = LabelStore.get_instance().get_label_pairs()
                    if labels:
                        self.report_controller.generate_report(labels)
                        print("[INFO] Report generation completed")
                    else:
                        print("[WARNING] No label pairs retrieved from database")

            except KeyboardInterrupt:
                print("\n[INFO] Evaluation System interrupted by user")
                break
            except Exception as e:
                print(f"[ERROR] Error in main loop: {e}")
                continue

        print("[INFO] Evaluation System shutting down...")
