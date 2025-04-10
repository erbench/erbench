import os
import requests
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
    filteringSlurmId: int
    matchingAlgoId: int
    matchingParams: Dict[str, Any]
    matchingSlurmId: int
    notifyEmail: str
    createdAt: str
    filteringAlgo: FilteringAlgo
    matchingAlgo: MatchingAlgo
    dataset: Dataset


class Metrics(TypedDict, total=False):
    filteringF1: Optional[float]
    filteringPrecision: Optional[float]
    filteringRecall: Optional[float]
    filteringTime: Optional[int]
    filteringCandidates: Optional[int]
    filteringEntriesA: Optional[int]
    filteringEntriesB: Optional[int]
    filteringMatches: Optional[int]
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


class JobStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    FILTERING = "filtering"
    MATCHING = "matching"
    COMPLETED = "completed"
    FAILED = "failed"


class Prediction(TypedDict):
    tableA_id: int
    tableB_id: int
    probability: float
    label: int


class ErbenchClient:

    def __init__(self):
        self.base_url = os.getenv("API_BASE_URL", "https://demo5.kbs.uni-hannover.de")
        self.api_key = os.getenv("API_KEY")

        if not self.base_url:
            raise ValueError("API_BASE_URL not found. Please create a .env file with API_BASE_URL defined.")

    def get_jobs(self) -> List[Job]:
        url = f"{self.base_url}/api/jobs"
        headers = self._get_headers()

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        json = response.json()
        if response.status_code == 200 and json['data']:
            return json['data']
        else:
            return []

    def update_job(self, job_id: str, status: JobStatus, filtering_slurm_id: int = None, matching_slurm_id: int = None) -> requests.Response:
        url = f"{self.base_url}/api/jobs/{job_id}"
        headers = self._get_headers()

        payload = {
            "status": status.value,
        }
        if filtering_slurm_id is not None:
            payload["filteringSlurmId"] = filtering_slurm_id
        if matching_slurm_id is not None:
            payload["matchingSlurmId"] = matching_slurm_id

        response = requests.put(url, headers=headers, json=payload)
        response.raise_for_status()
        return response

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
