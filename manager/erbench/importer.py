import os
import csv
import json
from typing import List

from .client import Metrics, Prediction


def import_filtering_results(directory: str, results: Metrics = None) -> Metrics | None:
    if results is None:
        results = Metrics()

    metrics_path = os.path.join(directory, "filtering_metrics.csv")
    if not os.path.exists(metrics_path):
        print(f"Error: {metrics_path} does not exist")
        return None

    try:
        with open(metrics_path, "r") as f:
            reader = csv.reader(f)
            headers = next(reader)
            values = next(reader)
            metrics = dict(zip(headers, values))

            results["filteringF1"] = float(metrics.get("f1", 0))
            results["filteringPrecision"] = float(metrics.get("precision", 0))
            results["filteringRecall"] = float(metrics.get("recall", 0))
            results["filteringTime"] = round(float(metrics.get("filtering_time", 0)) * 1000)
            results["filteringCandidates"] = int(metrics.get("num_candidates", 0))
            results["filteringEntriesA"] = int(metrics.get("entries_tableA", 0))
            results["filteringEntriesB"] = int(metrics.get("entries_tableB", 0))
            results["filteringMatches"] = int(metrics.get("entries_matches", 0))
    except Exception as e:
        print(f"Error reading filtering_metrics.csv: {e}")
        return None

    return results


def import_results(directory: str, results: Metrics = None) -> Metrics | None:
    if results is None:
        results = Metrics()

    metrics_path = os.path.join(directory, "metrics.csv")
    if not os.path.exists(metrics_path):
        print(f"Error: {metrics_path} does not exist")
        return None

    try:
        with open(metrics_path, "r") as f:
            reader = csv.reader(f)
            headers = next(reader)
            values = next(reader)
            metrics = dict(zip(headers, values))

            results["f1"] = float(metrics.get("f1", 0))
            results["precision"] = float(metrics.get("precision", 0))
            results["recall"] = float(metrics.get("recall", 0))
            results["trainTime"] = round(float(metrics.get("train_time", 0)) * 1000)
            results["evalTime"] = round(float(metrics.get("eval_time", 0)) * 1000)
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
        with open(predictions_path, "r") as f:
            reader = csv.reader(f)
            headers = next(reader)
            for row in reader:
                prediction_data = dict(zip(headers, row))
                predictions.append(
                    {
                        "tableA_id": int(prediction_data.get("tableA_id")),
                        "tableB_id": int(prediction_data.get("tableB_id")),
                        "label": int(prediction_data.get("label", 0)),
                        "probability": float(prediction_data.get("prob_class1", 0)),
                    }
                )
    except Exception as e:
        print(f"Error reading predictions.csv: {e}")
        return None

    return predictions


def import_slurm_metrics(job_json: str, results: Metrics = None) -> Metrics | None:
    if results is None:
        results = Metrics()

    try:
        job_data = json.loads(job_json)

        if not job_data.get("jobs") or len(job_data["jobs"]) == 0:
            print("Error: No jobs found in the job data")
            return None

        job = job_data["jobs"][0]

        if "time" in job and "elapsed" in job["time"]:
            results["totalRuntime"] = job["time"]["elapsed"] * 1000

        for jobTres in job.get("tres", {}).get("allocated", []):
            if jobTres.get("type") == "cpu":
                results["cpuAllocated"] = jobTres.get("count", 0)
            elif jobTres.get("type") == "gres" and jobTres.get("name") == "gpu":
                results["gpuAllocated"] = jobTres.get("count", 0)

        results["memUtilized"] = 0
        results["cpuUtilized"] = 0
        results["gpuUtilized"] = 0
        results["gpuMemUtilized"] = 0
        results["energyConsumed"] = 0

        for step in job.get("steps", []):
            if "time" in step and "total" in step["time"]:
                cpu_time = step["time"]["total"]
                results["cpuUtilized"] += cpu_time["seconds"] * 1000 + int(cpu_time.get("microseconds", 0) / 1000)

            for stepTres in step.get("tres", {}).get("requested", []).get("total", []):
                if stepTres.get("type") == "energy":
                    results["energyConsumed"] += stepTres.get("count", 0)
                elif stepTres.get("type") == "mem":
                    results["memUtilized"] += stepTres.get("count", 0)
                elif stepTres.get("type") == "gres" and stepTres.get("name") == "gpuutil":
                    results["gpuUtilized"] += stepTres.get("count", 0)
                elif stepTres.get("type") == "gres" and stepTres.get("name") == "gpumem":
                    results["gpuMemUtilized"] += stepTres.get("count", 0) // 1024 // 1024  # Convert to MB

    except json.JSONDecodeError as e:
        print(f"Error parsing job JSON: {e}")
        return None
    except Exception as e:
        print(f"Error processing Slurm metrics: {e}")
        return None

    return results
