import os

from config.constants import BEST_CLASSIFIER_FILE_PATH, BEST_CLASSIFIER_CSV_FILE_PATH
from model.report import Report

class ValidationReportGenerator:

    def __init__(self, best_classifiers):
        self._report = Report(best_classifiers)

    def generate_report(self):
        print("[INFO] Generate json report")
        self._report.generate_json(BEST_CLASSIFIER_FILE_PATH)
        print("[INFO] Json report generated")
        print("[INFO] Generate csv report")
        self._report.generate_csv(BEST_CLASSIFIER_CSV_FILE_PATH)
        print("[INFO] Csv report generated")
    