import os

from config.constants import TEST_RESULT_FILE_PATH, TEST_RESULT_CSV_FILE_PATH
from model.report import Report

class TestReportGenerator:

    def __init__(self, data):
        self._report = Report([data])

    def generate_test_report(self):
        self._report.generate_json(TEST_RESULT_FILE_PATH)
        self._report.generate_csv(TEST_RESULT_CSV_FILE_PATH)
