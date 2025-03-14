import os
import csv
from typing import List

from .client import Metrics, Prediction


def import_results(directory: str, results: Metrics = None) -> Metrics | None:
    if results is None:
        results = Metrics()

    metrics_path = os.path.join(directory, "metrics.csv")
    if not os.path.exists(metrics_path):
        print(f"Error: {metrics_path} does not exist")
        return None

    try:
        with open(metrics_path, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            values = next(reader)
            metrics = dict(zip(headers, values))

            results['f1'] = float(metrics.get("f1", 0))
            results['precision'] = float(metrics.get("precision", 0))
            results['recall'] = float(metrics.get("recall", 0))
            results['trainTime'] = round(float(metrics.get("train_time", 0)))
            results['evalTime'] = round(float(metrics.get("eval_time", 0)))
    except Exception as e:
        print(f"Error reading metrics.csv: {e}")
        return None

    return results


def import_predictions(directory: str) -> List[Prediction] | None:
    predictions_path = os.path.join(directory, "predictions.csv")
    if not os.path.exists(predictions_path):
        print(f"Error: {predictions_path} does not exist")
        return None

    predictions = []
    try:
        with open(predictions_path, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            for row in reader:
                prediction_data = dict(zip(headers, row))
                predictions.append({
                    "tableA_id": int(prediction_data.get("tableA_id")),
                    "tableB_id": int(prediction_data.get("tableB_id")),
                    "label": int(prediction_data.get("label", 0)),
                    "probability": float(prediction_data.get("prob_class1", 0)),
                })
    except Exception as e:
        print(f"Error reading predictions.csv: {e}")
        return None

    return predictions
