import os
import csv

from .client import ErbenchClient, JobStatus, Metrics


def import_results(job_id: str, directory: str, client: ErbenchClient, results = None) -> bool:
    """
    Reads metrics and predictions files from results directory and uploads to database.

    Args:
        job_id (str): The job ID
        directory (str): Path to directory containing metrics.csv and predictions.csv
        client (ErbenchClient): Instance of ErbenchClient to interact with the API
        results (Metrics, optional): Metrics object to populate with results

    Returns:
        bool: True if successful, False otherwise
    """
    metrics_path = os.path.join(directory, "metrics.csv")
    predictions_path = os.path.join(directory, "predictions.csv")

    if results is None:
        results = Metrics()

    if not os.path.exists(metrics_path):
        print(f"Error: {metrics_path} does not exist")
        return False

    if not os.path.exists(predictions_path):
        print(f"Error: {predictions_path} does not exist")
        return False

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
        return False

    # Read predictions from CSV file
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
        return False

    response = client.send_results(job_id, JobStatus.COMPLETED, results)
    if response.status_code != 200:
        print(f"Error sending results: {response.status_code}")
        return False

    predictions_response = client.send_predictions(job_id, predictions)
    if predictions_response.status_code != 200:
        print(f"Error sending predictions: {predictions_response.status_code}")
        return False

    return True
