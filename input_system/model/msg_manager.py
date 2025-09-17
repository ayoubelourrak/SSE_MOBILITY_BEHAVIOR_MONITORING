import os
import queue
import logging
from threading import Thread
from dotenv import load_dotenv
from flask import Flask, request
import requests

from log_service.log_service import RecordTimestampManager
from model.msg_configuration import MessageConfiguration
from marshmallow import Schema, fields

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
load_dotenv()

class LabelSchema(Schema):
    uuid = fields.String(required=True)
    label = fields.String(required=True)

class MessageManager:
    _instance = None

    def __init__(self):
        self._configuration = MessageConfiguration()
        self._app = Flask(__name__)
        self._queue = queue.Queue()
        self.database = RecordTimestampManager()

    @staticmethod
    def get_instance():
        if MessageManager._instance is None:
            MessageManager._instance = MessageManager()
        return MessageManager._instance

    def start_server(self):
        print("[INFO] Starting Rest server...")
        self._app.run(
            host = self._configuration.host_src_ip,
            port=self._configuration.host_src_port,
            debug=False,
        )
    def get_app(self):
        return self._app

    def get_queue(self):
        return self._queue

    def send_to_main(self):
        self._queue.put(True, block=True)

    def send_log(self, data):
        self.database.add_timestamp(data['uuid'], data['system_source'], data['timestamp'])

    def send_data(self, json):
        #uri = "http://" + self._configuration.host_dest_ip + ":" + str(self._configuration.host_dest_port) + "/record"
        ingestion_url = "http://" + self._configuration.host_dest_ip + ":" + str(self._configuration.host_dest_port) + "/record"
        try:
            res = requests.post(ingestion_url, json=json, timeout=3)
            if res.status_code != 200:
                raise Exception("[ERROR] Not received 200")
            self.database.add_timestamp(json['uuid'], 'input_system')
        except Exception as e:
            raise e
app = MessageManager.get_instance().get_app()

@app.get('/start')
def post_json():
    print("[INFO] Start msg received")
    receive_thread = Thread(target=MessageManager.get_instance().send_to_main)
    receive_thread.start()
    return {}, 200

@app.post("/label")
def post_label():
    schema = LabelSchema()
    errors = schema.validate(request.json)

    if errors:
        return errors, 400
    print(f"[INFO] Received Label: {request.json}")
    return {}, 200

@app.post("/evaluationReport")
def post_evaluation_report():
    print(f"[INFO] Received data from evaluation: {request.json}")
    return {}, 200

@app.post("/log")
def post_log():
    print(f"[INFO] Received Log: {request.json}")

    receive_thread = Thread(target=MessageManager.get_instance().send_log, args=(request.json,))
    receive_thread.start()
    return {}, 200
