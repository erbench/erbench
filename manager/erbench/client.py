import os
import requests
from dotenv import load_dotenv
from enum import Enum
from typing import List, TypedDict, Dict, Any, Optional


class FilteringAlgo(TypedDict):
    id: int
    code: str
    name: str
    scenarios: List[str]
    params: List[str]
    createdAt: str


class MatchingAlgo(TypedDict):
    id: int
    code: str
    name: str
    scenarios: List[str]
    params: List[str]
    createdAt: str


class Dataset(TypedDict):
    id: int
    code: str
    name: str
    hash: str
    isCustom: bool
    createdAt: str


class Job(TypedDict):
    id: str
    status: str
    datasetId: int
    filteringAlgoId: int
    filteringParams: Dict[str, Any]
    matchingAlgoId: int
    matchingParams: Dict[str, Any]
    notifyEmail: str
    createdAt: str
    filteringAlgo: FilteringAlgo
    matchingAlgo: MatchingAlgo
    dataset: Dataset


class Metrics(TypedDict, total=False):
    f1: Optional[float]
    precision: Optional[float]
    recall: Optional[float]
    trainTime: Optional[int]
    evalTime: Optional[int]
    cpuAllocated: Optional[int]
    cpuUtilized: Optional[int]
    memUtilized: Optional[int]
    gpuAllocated: Optional[int]
    gpuUtilized: Optional[int]
    gpuMemUtilized: Optional[int]
    energyConsumed: Optional[int]
    totalRuntime: Optional[int]


class JobStatus(Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Prediction(TypedDict):
    tableA_id: int
    tableB_id: int
    probability: float
    label: int


class ErbenchClient:

    def __init__(self):
        load_dotenv()

        self.base_url = os.getenv("API_BASE_URL")
        self.api_key = os.getenv("API_KEY")

        if not self.base_url:
            raise ValueError("API_BASE_URL not found. Please create a .env file with API_BASE_URL defined.")

    def get_jobs(self) -> List[Job]:
        url = f"{self.base_url}/api/jobs"
        headers = self._get_headers()

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return response.json()

    def send_results(self, job_id: str, status: JobStatus, metrics: Metrics) -> requests.Response:
        url = f"{self.base_url}/api/jobs/{job_id}/results"
        headers = self._get_headers()

        response = requests.put(url, headers=headers, json={
            "status": status.value,
            **metrics
        })
        response.raise_for_status()
        return response

    def send_predictions(self, job_id: str, predictions: List[Prediction]) -> requests.Response:
        url = f"{self.base_url}/api/jobs/{job_id}/predictions"
        headers = self._get_headers()

        response = requests.put(url, headers=headers, json=predictions)
        response.raise_for_status()
        return response

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
