import os
from utils.json_reader import JsonReader
from config.constants import CONFIG_FILE_PATH

class SystemConfiguration:

    def __init__(self):
        read_result, file_content = JsonReader.read_json_file(CONFIG_FILE_PATH)
        if not read_result:
            return
        self.starting_mode = file_content["starting-mode"]
        self.stage = file_content["stage"]
        self.ongoing_validation = file_content["ongoing-validation"]

    def update_stage(self):
        JsonReader.update_json_file(CONFIG_FILE_PATH , "stage" , self.stage)
