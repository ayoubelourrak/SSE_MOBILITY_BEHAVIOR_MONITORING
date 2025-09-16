from model.msg_configuration import MessageConfiguration
from utils.json_reader import JsonReader
import queue
from flask import Flask, request
from threading import Thread
import requests
from marshmallow import Schema, fields
from model.label import Label

class LabelSchema(Schema):
    uuid = fields.String(required=True)
    label = fields.String(required=True)


class MessageManager:
    _instance = None

    def __init__(self):
        self._configuration = MessageConfiguration()
        self.msg_config = self._configuration
        self._app = Flask(__name__)
        self._queue = queue.Queue()

    @staticmethod
    def get_instance():
        if MessageManager._instance is None:
            MessageManager._instance = MessageManager()
        return MessageManager._instance

    def start_server(self):
        print("[INFO] Starting Rest server...")
        self._app.run(
            host=self._configuration.host_src_ip,
            port=self._configuration.host_src_port,
            debug=False,
        )

    def get_app(self):
        return self._app

    def get_queue(self):
        return self._queue

    def send_to_main(self , received_label):
        label = Label(received_label)
        self._queue.put(label, block=True)
        print('[INFO] Label received')

    def send_start(self):
        self._queue.put(True, block=True)
        print('[INFO] Start message received')

    def send_report_to_orchestrator(self, json_report_path):
        """
        Send the evaluation report to the orchestrator system
        """
        try:
            print("[INFO] Sending evaluation report to orchestrator system...")

            # Read the JSON report
            read_success, report_data = JsonReader.read_json_file(json_report_path)
            if not read_success:
                print(f"[ERROR] Failed to read report file: {json_report_path}")
                return

            # Send to orchestrator
            orchestrator_url = f"http://{self.msg_config.host_dest_ip}:{self.msg_config.host_dest_port}/evaluationReport"

            response = requests.post(
                orchestrator_url,
                json=report_data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )

            if response.status_code == 200:
                print("[+] Successfully sent evaluation report to orchestrator")
            else:
                print(f"[ERROR] Failed to send report to orchestrator. Status: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Network error sending report to orchestrator: {e}")
        except Exception as e:
            print(f"[ERROR] Error sending report to orchestrator: {e}")

app = MessageManager.get_instance().get_app()

@app.get('/start')
def start_app():
    print("[INFO] Start msg received")
    receive_thread = Thread(target=MessageManager.get_instance().send_start)
    receive_thread.start()
    return {}, 200

@app.post("/classifierLabels")
def post_label():
    schema = LabelSchema()
    errors = schema.validate(request.json)

    if errors:
        return errors, 400
    print(f"[INFO] Received Label: {request.json} from production system")
    received_label = {
        "uuid": request.json["uuid"],
        "label": request.json["label"],
        "label_source": "production",
    }
    receive_thread = Thread(target=MessageManager.get_instance().send_to_main, args=(received_label,))
    receive_thread.start()
    return {}, 200

@app.post("/expertLabels")
def post_expert_label():
    schema = LabelSchema()
    errors = schema.validate(request.json)

    if errors:
        return errors, 400
    print(f"[INFO] Received Label: {request.json} from ingestion system")
    received_label = {
        "uuid": request.json["uuid"],
        "label": request.json["label"],
        "label_source": "ingestion",
    }
    receive_thread = Thread(target=MessageManager.get_instance().send_to_main, args=(received_label,))
    receive_thread.start()
    return {}, 200