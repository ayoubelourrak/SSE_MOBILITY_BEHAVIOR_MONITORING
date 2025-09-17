import os
import queue
import logging
import sys
from threading import Thread
from dotenv import load_dotenv
from flask import Flask, request
import requests
from datetime import datetime

from config.constants import CLASSIFIER_DIRECTORY_PATH
from model.msg_configuration import MessageConfiguration
from marshmallow import Schema, fields

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
load_dotenv()

class FeatureSchema(Schema):
    maximum_pressure_ts = fields.Float(required=True)
    minimum_pressure_ts = fields.Float(required=True)
    median_pressure_ts = fields.Float(required=True)
    mean_absolute_deviation_pressure_ts = fields.Float(required=True)
    activity_and_small_scatter = fields.Float(required=True)
    environment_and_small_scatter = fields.Float(required=True)
    label = fields.String(required=True)

class DataSchema(Schema):
    number_of_samples = fields.Int(required=True)
    features = fields.List(fields.Nested(FeatureSchema()))

class FullSchema(Schema):
    train = fields.Nested(DataSchema())
    validation = fields.Nested(DataSchema())
    test = fields.Nested(DataSchema())

class MessageManager:
    _instance = None

    def __init__(self):
        self._configuration = MessageConfiguration()
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
            host = self._configuration.host_src_ip,
            port=self._configuration.host_src_port,
            debug=False,
        )
    def get_app(self):
        return self._app

    def get_queue(self):
        return self._queue

    def send_to_main(self , dataset):
        self._queue.put(dataset, block=True)
        print('[INFO] Dataset received')

    def send_start(self):
        self._queue.put(True, block=True)
        print('[INFO] Start message received')

    def send_classifier(self , uuid):
        url = f"http://{self._configuration.host_dest_ip}:{self._configuration.host_dest_port}/deploy"
        file_path = CLASSIFIER_DIRECTORY_PATH + uuid + ".joblib"
        file = {'file': open(file_path,'rb')}
        self.send_log('all')

        try:
            r = requests.post(url, files=file , timeout=3)
            if r.status_code == 200:
                print("[INFO] Correctly deployed classifier")
            else:
                print("[ERROR] Impossible to deploy classifier")
                raise Exception("Impossible to deploy classifier")
        except TimeoutError:
            print("[ERROR] Timeout")
            raise TimeoutError

    def send_log(self, uuid:str) -> None:
        data = {
            'uuid': uuid,
            'system_source': 'development',
            'timestamp': datetime.now().isoformat()
        }
        connection_string = f'http://{self._configuration.host_log_ip}:{self._configuration.host_log_port}/log'
        print(f'[INFO] Send log: {data} to {connection_string}')
        try:
            response = requests.post(url=connection_string, json=data, timeout=3)
            if response.status_code != 200:
                error_message = response.json()['error']
                print(f'[ERROR] error: {error_message}')
        except Exception as e:
            print(f'[ERROR] log unreachable for {uuid} caused error: {e}')

app = MessageManager.get_instance().get_app()

@app.get('/start')
def start_app():
    print("[INFO] Start msg received")
    receive_thread = Thread(target=MessageManager.get_instance().send_start)
    receive_thread.start()
    return {}, 200

@app.post('/senddata')
def post_json():
    if request.json is None:
        return {'error': 'No Payload Received'}, 500

    received_json = request.json

    schema = FullSchema()
    errors = schema.validate(received_json)

    if errors:
        return errors, 400

    print("[INFO] Received payload validated")
    receive_thread = Thread(target=MessageManager.get_instance().send_to_main, args=(received_json,))
    receive_thread.start()
    return {}, 200
