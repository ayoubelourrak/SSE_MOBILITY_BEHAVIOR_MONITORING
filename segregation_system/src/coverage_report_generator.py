import os
import json
import plotly.graph_objects as go
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from jsonschema import validate, ValidationError

class CoverageReportGenerator:

    def __init__(self):
        pass

    def generate_chart(self, dataset):

        # Get data from the prepared sessions
        maximum_pressure_ts = []
        minimum_pressure_ts = []
        median_pressure_ts = []
        mean_absolute_deviation_pressure_ts = []
        activity_and_small_scatter = []
        environment_and_small_scatter = []

        # prepare data to build the chart
        for prepared_session in dataset:
            maximum_pressure_ts.append(prepared_session['features']['maximum_pressure_ts'])
            minimum_pressure_ts.append(prepared_session['features']['minimum_pressure_ts'])
            median_pressure_ts.append(prepared_session['features']['median_pressure_ts'])
            mean_absolute_deviation_pressure_ts.append(
                prepared_session['features']['mean_absolute_deviation_pressure_ts'])
            activity_and_small_scatter.append(
                prepared_session['features']['activity_and_small_scatter'])
            environment_and_small_scatter.append(
                prepared_session['features']['environment_and_small_scatter'])

        feature_lists = [
            maximum_pressure_ts,
            minimum_pressure_ts,
            median_pressure_ts,
            mean_absolute_deviation_pressure_ts,
            activity_and_small_scatter,
            environment_and_small_scatter
        ]

        feature_names = [
            'Maximum Pressure TS',
            'Minimum Pressure TS',
            'Median Pressure TS',
            'Mean Abs Dev Pressure TS',
            'Activity & Small Scatter',
            'Environment & Small Scatter'
        ]

        # Convert feature lists to array and transpose
        X = np.array(feature_lists).T
        X_original = X.copy()

        # Scale features to 0-1 range for better radar visualization
        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(X)

        fig = go.Figure()

        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

        # Add scatter points for each feature
        for feat_idx, feature_name in enumerate(feature_names):
            feature_color = colors[feat_idx % len(colors)]

            # Get all scaled values for this feature
            feature_values = X_scaled[:, feat_idx]

            # Create scatter plot for this feature
            fig.add_trace(go.Scatterpolar(
                r=feature_values,
                theta=[feature_name] * len(feature_values),
                mode='markers',
                name=feature_name,
                marker=dict(
                    size=6,
                    color=feature_color,
                    opacity=0.7
                ),
                hovertemplate=f'<b>{feature_name}</b><br>Scaled Value: %{{r:.3f}}<extra></extra>'
            ))

        # Calculate original min/max for each feature
        feature_info = []
        coverage_stats = {}

        for i, name in enumerate(feature_names):
            original_values = X_original[:, i]
            min_val = np.min(original_values)
            max_val = np.max(original_values)
            coverage = np.ptp(X_scaled[:, i])

            feature_info.append(f"{name}: [{min_val:.2f}, {max_val:.2f}]")
            coverage_stats[name] = coverage

        # Create legend text with min/max ranges
        legend_text = '<br>'.join(feature_info)

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[-0.1, 1.1],
                    tickvals=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
                    tickfont=dict(size=10)
                ),
                angularaxis=dict(tickfont=dict(size=12))
            ),
            title=dict(text="Features Coverage", x=0.5, font=dict(size=16)),
            annotations=[
                dict(
                    text=f"<b>Feature Ranges (Original Values):</b><br>{legend_text}",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=1.02, y=0.8, xanchor="left", yanchor="top",
                    bgcolor="rgba(255,255,255,0.9)",
                    bordercolor="black", borderwidth=1,
                    font=dict(size=10)
                )
            ],
            width=1500, height=900,
            margin=dict(r=150),
            showlegend=True
        )

        chart_path = os.path.join(os.path.abspath('.'), 'data', 'coverage', 'coverage_chart.png')
        # save chart as png image
        try:
            fig.write_image(chart_path)
            print('Coverage chart generated')
        except Exception as e:
            print(e)
            print('Failed to save the coverage chart')
            return None


        # Get the info for the report
        info = dict()
        info['maximum_pressure_ts'] = maximum_pressure_ts
        info['minimum_pressure_ts'] = minimum_pressure_ts
        info['median_pressure_ts'] = median_pressure_ts
        info['mean_absolute_deviation_pressure_ts'] = mean_absolute_deviation_pressure_ts
        info['activity_and_small_scatter'] = activity_and_small_scatter
        info['environment_and_small_scatter'] = environment_and_small_scatter

        return info

    def generate_report(self, info):

        # Handle human interaction
        print("Analize 'coverage_chart.png'")
        print("Answer only 'ok' or 'not ok")
        evaluation = input('> ')
        if evaluation == 'ok':
            info['evaluation'] = 'ok'
        else:
            info['evaluation'] = 'not ok'


        # save a report with the evaluation that a human will make
        report_path = os.path.join(os.path.abspath('.'), 'data', 'coverage',
                                   'coverage_report.json')
        try:
            with open(report_path, "w") as file:
                json.dump(info, file, indent=4)
        except Exception as e:
            print(e)
            print("Failure to save coverage_report.json")
            return False
        return True

    def evaluate_report(self):

        report_path = os.path.join(os.path.abspath('.'), 'data', 'coverage',
                                   'coverage_report.json')
        schema_path = os.path.join(os.path.abspath('.'), 'schemas', 'coverage_report_schema.json')

        # open the report file and validate it
        try:
            with open(report_path) as file:
                report = json.load(file)

            with open(schema_path) as file:
                report_schema = json.load(file)

            validate(report, report_schema)

        except FileNotFoundError:
            print('Failure to open coverage_report.json')
            return -2

        except ValidationError:
            print('Coverage Report has invalid schema')
            return -2

        # Read human evaluation
        evaluation = report['evaluation']

        if evaluation == 'ok':
            print("Coverage evaluation: ok")
            return 0
        elif evaluation == 'not ok':
            print("Coverage evaluation: not ok")
            return -1
        else:
            print("[!] Coverage evaluation non done")
            return -2
        