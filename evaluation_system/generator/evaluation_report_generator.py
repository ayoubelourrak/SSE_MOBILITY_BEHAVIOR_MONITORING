import matplotlib.pyplot as plt
import os
from datetime import datetime
from model.evaluation_report import EvaluationReport


class EvaluationReportGenerator:

    def __init__(self):
        self.output_dir = "reports"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_png_table(self, evaluation_report: EvaluationReport, filename_prefix="evaluation_report"):
        """
        Generate a PNG table visualization of the evaluation report
        """
        try:
            # Create figure with wider layout to accommodate side-by-side content
            fig, (ax_summary, ax_table) = plt.subplots(1, 2, figsize=(18, max(8, int(len(
                evaluation_report.label_comparison_results) * 0.4 + 3))))

            # Configure summary axis (left side)
            ax_summary.axis('off')
            ax_summary.set_xlim(0, 1)
            ax_summary.set_ylim(0, 1)

            # Configure table axis (right side)
            ax_table.axis('tight')
            ax_table.axis('off')

            # Prepare table data
            headers = ['UUID', 'Expert Label', 'Classifier Label', 'Status']
            table_data = []

            for comparison in evaluation_report.label_comparison_results:
                status = 'ERROR' if comparison['is_error'] else 'MATCH'
                table_data.append([
                    comparison['uuid'],
                    comparison['expert_label'],
                    comparison['classifier_label'],
                    status
                ])

            # Create table on the right side
            table = ax_table.table(cellText=table_data,
                                   colLabels=headers,
                                   cellLoc='center',
                                   loc='center',
                                   bbox=[0, 0, 1, 1])

            # Style the table
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 2)

            # Color code the cells
            for i in range(len(table_data)):
                for j in range(len(headers)):
                    cell = table[(i + 1, j)]
                    if j == 3:  # Status column
                        if 'ERROR' in table_data[i][j]:
                            cell.set_facecolor('#ffcccc')  # Light red for errors
                        else:
                            cell.set_facecolor('#ccffcc')  # Light green for matches

            # Style header
            for j in range(len(headers)):
                table[(0, j)].set_facecolor('#4472C4')
                table[(0, j)].set_text_props(weight='bold', color='white')

            # Add summary information on the left side
            summary_text = f"""Evaluation Report Summary
                Generated: {evaluation_report.report_timestamp}
            
                Total Labels: {evaluation_report.total_labels}
                Total Errors: {evaluation_report.total_errors}
                Error Rate: {evaluation_report.total_errors / evaluation_report.total_labels * 100:.1f}%
                Max Consecutive Errors: {evaluation_report.max_consecutive_error_count}
            
                Thresholds:
                - Max Errors: {evaluation_report.max_errors}
                - Max Consecutive Errors: {evaluation_report.max_consecutive_errors}
            
                Status: {'VALID' if evaluation_report.is_valid else 'INVALID'}"""

            ax_summary.text(0.05, 0.95, summary_text, transform=ax_summary.transAxes, fontsize=12,
                            verticalalignment='top', horizontalalignment='left',
                            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

            # Adjust layout to prevent overlap
            plt.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02, wspace=0.1)

            # Save the plot
            filename = f"{filename_prefix}.png"
            filepath = os.path.join(self.output_dir, filename)

            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()

            print(f"[+] PNG report saved to: {filepath}")
            return filepath

        except Exception as e:
            print(f"[ERROR] Failed to generate PNG report: {e}")
            return None

    def generate_json_report(self, evaluation_report: EvaluationReport, filename_prefix="evaluation_report"):
        """
        Generate a JSON report file
        """
        try:
            filename = f"{filename_prefix}.json"
            filepath = os.path.join(self.output_dir, filename)

            if evaluation_report.save_to_file(filepath):
                print(f"[+] JSON report saved to: {filepath}")
                return filepath
            else:
                return None

        except Exception as e:
            print(f"[ERROR] Failed to generate JSON report: {e}")
            return None

    def generate_reports(self, evaluation_report: EvaluationReport):
        """
        Generate both JSON and PNG reports
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = self.generate_json_report(evaluation_report, f"evaluation_report_{timestamp}")
        png_path = self.generate_png_table(evaluation_report, f"evaluation_report_{timestamp}")

        return {
            'json_path': json_path,
            'png_path': png_path,
            'timestamp': timestamp
        }
