from config.constants import CONFIG_FILE_PATH
from utils.json_reader import JsonReader


class SystemConfiguration:

    def __init__(self):
        read_result, file_content = JsonReader.read_json_file(CONFIG_FILE_PATH)
        if not read_result:
            return
        self.report_size = file_content["report-size"]
        self.max_errors = file_content["max-errors"]
        self.max_consecutive_errors = file_content["max-consecutive-errors"]
        self.db_name = file_content["db-name"]