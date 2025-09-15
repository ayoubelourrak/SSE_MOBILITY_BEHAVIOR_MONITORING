import os

from config.constants import CONFIG_FILE_PATH
from utils.json_reader import JsonReader

class SystemConfiguration:

    def __init__(self):
        read_result, file_content = JsonReader.read_json_file(CONFIG_FILE_PATH)
        if not read_result:
            return
        self.evaluation_phase = bool(int(os.getenv("EVALUATION_PHASE")))
        print(f"Evaluation Phase: {self.evaluation_phase}")
        print(type(self.evaluation_phase))
        self.classifier_deployed = bool(os.getenv("CLASSIFIER_DEPLOYED"))
    
    def update_classifier(self , value):
        self.classifier_deployed = value