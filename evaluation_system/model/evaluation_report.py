import datetime
from utils.json_reader import JsonReader


class EvaluationReport:

    def __init__(self, labels, max_errors, max_consecutive_errors):
        self.labels = labels
        self.max_errors = max_errors
        self.max_consecutive_errors = max_consecutive_errors
        self.total_labels = len(labels)
        self.total_errors = 0
        self.max_consecutive_error_count = 0
        self.label_comparison_results = []
        self.report_timestamp = datetime.datetime.now().isoformat()
        self.is_valid = True

        self._analyze_labels()

    def _analyze_labels(self):
        consecutive_errors = 0
        max_consecutive = 0

        for label_pair in self.labels:
            is_error = label_pair['label_ingestion'] != label_pair['label_production']

            comparison_result = {
                'uuid': label_pair['uuid'],
                'expert_label': label_pair['label_ingestion'],
                'classifier_label': label_pair['label_production'],
                'is_error': is_error
            }
            self.label_comparison_results.append(comparison_result)

            if is_error:
                self.total_errors += 1
                consecutive_errors += 1
                max_consecutive = max(max_consecutive, consecutive_errors)
            else:
                consecutive_errors = 0

        self.max_consecutive_error_count = max_consecutive

        # Check if report is valid based on thresholds
        self.is_valid = (self.total_errors <= self.max_errors and
                        self.max_consecutive_error_count <= self.max_consecutive_errors)

    def to_json(self):
        return {
            "report_timestamp": self.report_timestamp,
            "total_labels": self.total_labels,
            "total_errors": self.total_errors,
            "max_consecutive_errors_found": self.max_consecutive_error_count,
            "max_errors_threshold": self.max_errors,
            "max_consecutive_errors_threshold": self.max_consecutive_errors,
            "is_valid": self.is_valid,
            "label_comparisons": self.label_comparison_results
        }

    def save_to_file(self, file_path):
        return JsonReader.write_json_file(file_path, self.to_json())

    def get_summary(self):
        return {
            "total_labels": self.total_labels,
            "total_errors": self.total_errors,
            "error_rate": self.total_errors / self.total_labels if self.total_labels > 0 else 0,
            "max_consecutive_errors": self.max_consecutive_error_count,
            "is_valid": self.is_valid
        }