import os
import json
import plotly.graph_objects as go
from jsonschema import validate, ValidationError

class BalancingReportGenerator:

    def __init__(self):
        pass

    def generate_chart(self, dataset, balancing_tolerance=10.0):

        items = ['Shopping', 'Sport', 'Cooking', 'Gaming']
        values = [0,0,0,0]
        activity_mapping = {
            'shopping': 0,
            'sport': 1,
            'cooking': 2,
            'gaming': 3
        }

        # Count instances for each class
        for prepared_session in dataset:
            activity = prepared_session['calendar'].lower()
            if activity in activity_mapping:
                values[activity_mapping[activity]] += 1

        total_activities = sum(values)

        # Calculate average number of instances per class
        num_classes = len(items)
        average_instances = total_activities / num_classes if num_classes > 0 else 0

        # Calculate balancing tolerance threshold
        tolerance_absolute = (balancing_tolerance / 100.0) * average_instances
        min_threshold = average_instances - tolerance_absolute
        max_threshold = average_instances + tolerance_absolute

        # Check if classes are balanced
        is_balanced = all(min_threshold <= count <= max_threshold for count in values)

        # Calculate deviations from average
        deviations = []
        percentage_deviations = []
        for count in values:
            deviation = abs(count - average_instances)
            deviations.append(deviation)

            if average_instances > 0:
                percentage_deviation = (deviation / average_instances) * 100
            else:
                percentage_deviation = 0
            percentage_deviations.append(percentage_deviation)

        # Create the bar chart
        fig = go.Figure()

        # Add bars with color coding based on balance status
        colors = []
        for count in values:
            if min_threshold <= count <= max_threshold:
                colors.append('green')  # Within tolerance
            else:
                colors.append('red')  # Outside tolerance

        fig.add_trace(
            go.Bar(
                x=items,
                y=values,
                marker_color=colors,
                text=values,
                textposition='auto'
            )
        )

        # Add horizontal lines for thresholds
        fig.add_hline(y=average_instances,
                      line_dash="solid",
                      line_color="blue",
                      annotation_text="Average")
        fig.add_hline(y=max_threshold,
                      line_dash="dash",
                      line_color="orange",
                      annotation_text=f"Max (+{balancing_tolerance}%)")
        fig.add_hline(y=min_threshold,
                      line_dash="dash",
                      line_color="orange",
                      annotation_text=f"Min (-{balancing_tolerance}%)")

        # Update layout
        fig.update_layout(
            title=f'Class Distribution - {"Balanced" if is_balanced else "Imbalanced"} '
                  f'(Tolerance: {balancing_tolerance}%)',
            xaxis_title='Activity Classes',
            yaxis_title='Number of Instances',
            showlegend=False
        )

        # Prepare comprehensive information dictionary
        info = {
            # Basic counts
            'shopping_items_number': values[0],
            'sport_items_number': values[1],
            'cooking_items_number': values[2],
            'gaming_items_number': values[3],
            'total_instances': total_activities,

            # Proportions
            'shopping_proportion': values[0] / total_activities if total_activities > 0 else 0,
            'sport_proportion': values[1] / total_activities if total_activities > 0 else 0,
            'cooking_proportion': values[2] / total_activities if total_activities > 0 else 0,
            'gaming_proportion': values[3] / total_activities if total_activities > 0 else 0,

            # Balancing analysis
            'is_balanced': is_balanced,
            'balancing_tolerance_percent': balancing_tolerance,
            'average_instances_per_class': average_instances,
            'tolerance_absolute': tolerance_absolute,
            'min_threshold': min_threshold,
            'max_threshold': max_threshold,

            # Deviations
            'deviations_from_average': dict(zip(items, deviations)),
            'percentage_deviations': dict(zip(items, percentage_deviations)),
            'max_deviation_percent': max(percentage_deviations) if percentage_deviations else 0,

            # Recommendations
            'classes_needing_more_data': [items[i] for i, count in enumerate(values)
                                          if count < min_threshold],
            'classes_with_excess_data': [items[i] for i, count in enumerate(values)
                                         if count > max_threshold]
        }

        # Save bar chart
        chart_path = os.path.join(os.path.abspath('.'), 'data', 'balancing', 'balancing_chart.png')
        try:
            fig.write_image(chart_path)
            print(f'Balance chart saved to: {chart_path}')
        except Exception as e:
            print(f'Failed to save the balance chart: {e}')
            return None

        # Print balancing status
        print(f'Balance check completed:')
        print(f'  Classes are {"BALANCED" if is_balanced else "IMBALANCED"}')
        print(f'  Tolerance: {balancing_tolerance}%')
        print(f'  Average instances per class: {average_instances:.1f}')
        print(f'  Max deviation: {info["max_deviation_percent"]:.1f}%')

        if not is_balanced:
            print(f'  Classes needing more data: {info["classes_needing_more_data"]}')
            print(f'  Classes with excess data: {info["classes_with_excess_data"]}')

        return info

    # TODO gestire meglio gli errori
    def generate_report(self, info):

        no_stop = bool(int(os.getenv('NO_STOP')))

        if no_stop:
            # Get value from the info
            evaluation = 'balanced' if info["is_balanced"] else 'not balanced'
            print(f"evaluation given by the info: {evaluation}")
        else:
            # Handle human interaction
            print("Analize 'balancing_chart.png'")
            print("Answer only 'balanced' or 'not balanced'")
            evaluation = input('> ')
        if evaluation == 'balanced':
            info['evaluation'] = 'balanced'
        else:
            info['evaluation'] = 'not balanced'

        # Save the report in a json file
        report_path = os.path.join(os.path.abspath('.'), 'data', 'balancing',
                                   'balancing_report.json')
        try:
            with open(report_path, "w") as file:
                json.dump(info, file, indent=4)
        except Exception as e:
            print(e)
            print('Failure to save balancing_report.json')
            return False

        print('Balancing report generated')
        return True

    def evaluate_report(self):

        report_path = os.path.join(os.path.abspath('.'), 'data', 'balancing',
                                   'balancing_report.json')
        schema_path = os.path.join(os.path.abspath('.'), 'schemas', 'balancing_report_schema.json')

        # open chart and validate it
        try:
            with open(report_path) as file:
                report = json.load(file)

            with open(schema_path) as file:
                report_schema = json.load(file)

            validate(report, report_schema)

        except FileNotFoundError:
            print('Failure to open balancing_report.json')
            return -2

        except ValidationError:
            print('Balancing Report has invalid schema')
            return -2

        # Read human evaluation
        evaluation = report['evaluation']

        if evaluation == 'balanced':
            print("Balancing evaluation: Dataset balanced")
            return 0
        elif evaluation == 'not balanced':
            print("Balancing evaluation: Dataset not balanced")
            return -1

        else:
            print("Balancing evaluation not done")
            return -2
        