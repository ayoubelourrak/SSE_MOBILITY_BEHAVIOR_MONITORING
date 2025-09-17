import os
import random

from controller.label_store_controller import LabelStore
from model.evaluation_report import EvaluationReport
from model.msg_manager import MessageManager
from model.system_configuration import SystemConfiguration
from model.msg_configuration import MessageConfiguration
from generator.evaluation_report_generator import EvaluationReportGenerator


class ReportController:

    def __init__(self):
        self.system_config = SystemConfiguration()
        self.msg_config = MessageConfiguration()
        self.report_generator = EvaluationReportGenerator()

    def generate_report(self, labels):
        """
        Generate evaluation report from label pairs
        """
        print(f"[INFO] Generating evaluation report for {len(labels)} label pairs")

        # Create evaluation report
        evaluation_report = EvaluationReport(
            labels=labels,
            max_errors=self.system_config.max_errors,
            max_consecutive_errors=self.system_config.max_consecutive_errors
        )

        # Generate report files (JSON and PNG)
        report_files = self.report_generator.generate_reports(evaluation_report)

        # Display report summary
        summary = evaluation_report.get_summary()
        print("\n" + "="*50)
        print("EVALUATION REPORT SUMMARY")
        print("="*50)
        print(f"Total Labels: {summary['total_labels']}")
        print(f"Total Errors: {summary['total_errors']}")
        print(f"Error Rate: {summary['error_rate']:.2%}")
        print(f"Max Consecutive Errors: {summary['max_consecutive_errors']}")
        print(f"Status: {'VALID' if summary['is_valid'] else 'INVALID'}")
        print("="*50)

        if report_files['json_path']:
            print(f"JSON Report: {report_files['json_path']}")
        if report_files['png_path']:
            print(f"PNG Report: {report_files['png_path']}")

        # Ask user for approval
        user_approval = self._get_user_approval()

        if user_approval:
            print("[INFO] User approved the evaluation report")
        else:
            print("[INFO] User rejected the evaluation report")
            # Send report to orchestrator system
            if report_files['json_path']:
                MessageManager.get_instance().send_report_to_orchestrator(report_files['json_path'])

        # Remove processed labels from database
        label_ids = [label['uuid'] for label in labels]
        LabelStore.get_instance().remove_labels(label_ids)
        print("[INFO] Processed labels removed from database")

        return evaluation_report

    def _get_user_approval(self):
        """
        Get user approval for the evaluation report
        """
        while True:
            try:
                print("\n" + "-"*40)
                print("REPORT REVIEW")
                print("-"*40)
                print("Please review the evaluation report.")
                print("The JSON and PNG files have been generated.")
                print("\nIs this evaluation report acceptable?")
                no_stop = bool(int(os.getenv('NO_STOP')))
                if no_stop:
                    response = random.choices(['y', 'n'], weights=[0.01, 0.99], k=1)[0]
                else:
                    response = input("Enter 'y' for yes, 'n' for no: ").lower().strip()

                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no']:
                    return False
                else:
                    print("Please enter 'y' for yes or 'n' for no.")

            except KeyboardInterrupt:
                print("\n[INFO] User interrupted. Treating as rejection.")
                return False
            except Exception as e:
                print(f"[ERROR] Error getting user input: {e}")
                return False