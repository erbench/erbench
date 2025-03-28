import argparse
import json
import os
import shutil
import tempfile
import pathtype
import subprocess
from dotenv import load_dotenv

load_dotenv()

from erbench.client import ErbenchClient, JobStatus, Job
from erbench.importer import import_results, import_slurm_metrics
from manager.erbench.importer import import_predictions

DATASETS_DIR = os.getenv("DATASETS_DIR", "../datasets")
CONTAINERS_DIR = os.getenv("CONTAINERS_DIR", "../apptainer")
TEMP_DIR = os.getenv("TEMP_DIR", "../running_jobs")

# loads configuration from .env file
erbench_client = ErbenchClient()


def import_job(job_id: str, input_dir: any, slurm_job_id: int = None):
    print(f"Importing results for job {job_id} from {input_dir}")

    slurm_job_str = None
    if slurm_job_id:
        try:
            print(f"Retrieving Slurm metrics for job {slurm_job_id}")
            process = subprocess.run(['sacct', '-j', str(slurm_job_id), '--json'], capture_output=True, text=True)
            if process.returncode == 0:
                slurm_job_str = process.stdout
            else:
                print(f"Warning: Failed to retrieve Slurm metrics: {process.stderr}")
        except Exception as e:
            print(f"Warning: Error retrieving Slurm metrics: {str(e)}")

    results = import_results(input_dir)
    if not results: exit(1)

    if slurm_job_str:
        results = import_slurm_metrics(slurm_job_str, results)
        print("Slurm metrics retrieved successfully")

    erbench_client.send_results(job_id, JobStatus.COMPLETED, results)
    print("Results upload completed successfully")

    predictions = import_predictions(input_dir)
    if not predictions: exit(1)

    erbench_client.send_predictions(job_id, predictions)
    print("Predictions upload completed successfully")


def get_job_directory(job_id: str) -> str:
    return os.path.join(TEMP_DIR, f"erbench_job_{job_id}")


def start_job(job: Job):
    dataset_path = os.path.join(DATASETS_DIR, job['dataset']['code'])
    if not os.path.exists(dataset_path):
        raise RuntimeError(f"Dataset directory {dataset_path} does not exist")

    filtering_container = os.path.join(CONTAINERS_DIR, f"{job['filteringAlgo']['code']}.sif")
    if not os.path.exists(filtering_container):
        raise RuntimeError(f"Error: Filtering algorithm container {filtering_container} does not exist, skipping job")

    matching_container = os.path.join(CONTAINERS_DIR, f"{job['matchingAlgo']['code']}.sif")
    if not os.path.exists(matching_container):
        raise RuntimeError(f"Error: Matching algorithm container {matching_container} does not exist, skipping job")

    try:
        job_dir = get_job_directory(job['id'])
        print(f"Creating job directory: {job_dir}")
        os.makedirs(job_dir, exist_ok=True)

        # print(f"Copying dataset files from {dataset_path} to {job_dir}")
        # for item in os.listdir(dataset_path):
        #     shutil.copy2(os.path.join(dataset_path, item), os.path.join(job_dir, item))

        filtering_params_str = ' '.join([f'--{k}={v}' for k, v in job['filteringParams'].items()])
        print(f"Starting filtering job {job['filteringAlgo']['code']} with params: {filtering_params_str}")
        filtering_cmd = f"sbatch --parsable -p ampere --gpus=1 -o {job_dir}/filtering.out -e {job_dir}/filtering.err "
        filtering_cmd += f"--wrap=\"apptainer run {filtering_container} {dataset_path} {job_dir} {filtering_params_str}\""

        process = subprocess.run(filtering_cmd, shell=True, capture_output=True, text=True)
        if process.returncode != 0:
            raise RuntimeError(f"Error running filtering job: {process.stderr}")

        filtering_job_id = process.stdout.strip()
        print(f"Filtering job submitted with ID: {filtering_job_id}")

        matching_params_str = ' '.join([f'--{k}={v}' for k, v in job['matchingParams'].items()])
        print(f"Starting matching job {job['matchingAlgo']['code']} with params: {matching_params_str}")
        matching_cmd = f"sbatch --parsable -p ampere --gpus=1 -o {job_dir}/matching.out -e {job_dir}/matching.err --dependency=afterok:{filtering_job_id}"
        matching_cmd += f"--wrap=\"apptainer run {matching_container} {job_dir} {matching_params_str}\""

        process = subprocess.run(matching_cmd, shell=True, capture_output=True, text=True)
        if process.returncode != 0:
            raise RuntimeError(f"Error running matching job: {process.stderr}")

        matching_job_id = process.stdout.strip()
        print(f"Matching job submitted with ID: {matching_job_id}")

        erbench_client.update_job(job['id'], JobStatus.RUNNING, filtering_job_id, matching_job_id)
        print(f"Job {job['id']} updated to RUNNING status with filtering job ID {filtering_job_id} and matching job ID {matching_job_id}")
    except Exception as e:
        print(f"Error executing job: {str(e)}")


def check_job(job: Job):
    filtering_job_id = job['filteringSlurmId']
    matching_job_id = job['matchingSlurmId']

    try:
        filtering_process = subprocess.run(['sacct', '-j', str(filtering_job_id), '--format=State'], capture_output=True, text=True)
        if filtering_process.returncode != 0:
            raise RuntimeError(f"Error checking filtering job status: {filtering_process.stderr}")

        matching_process = subprocess.run(['sacct', '-j', str(matching_job_id), '--format=State'], capture_output=True, text=True)
        if matching_process.returncode != 0:
            raise RuntimeError(f"Error checking matching job status: {matching_process.stderr}")

        filtering_status = filtering_process.stdout.strip().split('\n')[-1]
        matching_status = matching_process.stdout.strip().split('\n')[-1]

        print(f"Filtering job {filtering_job_id} status: {filtering_status}")
        print(f"Matching job {matching_job_id} status: {matching_status}")

        if filtering_status == 'COMPLETED' and matching_status == 'COMPLETED':
            job_dir = get_job_directory(job['id'])
            print(f"Importing results for job {job['id']} from {job_dir}")
            import_job(job['id'], job_dir, matching_job_id)
        elif filtering_status == 'FAILED' or matching_status == 'FAILED':
            erbench_client.update_job(job['id'], JobStatus.FAILED)
            print(f"Job {job['id']} failed")
    except Exception as e:
        print(f"Error checking job status: {str(e)}")


def run_job():
    jobs = erbench_client.get_jobs()
    for job in jobs:
        try:
            print(f"Job: {json.dumps(job)}")
            if job['status'] == JobStatus.PENDING:
                print(f"Starting job {job['id']}")
                start_job(job)
            elif job['status'] == JobStatus.RUNNING:
                print(f"Checking job {job['id']}")
                check_job(job)
        except Exception as e:
            print(f"Error processing job {job['id']}: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ERBench Manager CLI')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    import_parser = subparsers.add_parser('import', help='Import results into database')
    import_parser.add_argument('job_id', type=str, help='The job ID in the ERBench database')
    import_parser.add_argument('input_dir', type=pathtype.Path(readable=True), help='The input directory containing the results')
    import_parser.add_argument('-sj', '--slurm-job-id', type=int, default=None, help='Slurm job ID, used to gather utilization metrics')
    import_parser.set_defaults(func=import_job)

    run_parser = subparsers.add_parser('run', help='Run entity resolution tasks')
    run_parser.set_defaults(func=run_job)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        arg_dict = vars(args).copy()
        arg_dict.pop('func')
        arg_dict.pop('command', None)
        args.func(**arg_dict)
    else:
        parser.print_help()
        exit(1)
