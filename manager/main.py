import argparse
import os
import shutil
import pathtype
import subprocess
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

from erbench.client import ErbenchClient, JobStatus, Job
from erbench.importer import import_results, import_slurm_metrics, import_predictions, import_filtering_results

ERBENCH_URL = os.getenv("API_BASE_URL", "https://demo5.kbs.uni-hannover.de")
DATASETS_DIR = os.getenv("DATASETS_DIR", "../datasets")
CONTAINERS_DIR = os.getenv("CONTAINERS_DIR", "../apptainer")
EMBEDDINGS_DIR = os.getenv("EMBEDDINGS_DIR", "../embeddings")
TEMP_DIR = os.getenv("TEMP_DIR", "../running_jobs")
SLURM_JOB_ARGS = os.getenv("SLURM_JOB_ARGS", "")

# loads configuration from .env file
erbench_client = ErbenchClient()


def is_gpu_required(algoCode: str) -> bool:
    if algoCode in ["splitter_random", "magellan", "zeroer"]:
        return False
    return True


def is_embeddings_required(algoCode: str) -> bool:
    if algoCode in ["deepmatcher", "hiermatcher", "splitter_deepblocker"]:
        return True
    return False


def render_params(params: dict) -> str:
    return " ".join([f"--{k}" if v is True else f'--{k}="{v}"' if isinstance(v, str) and " " in v else f"--{k}={v}" for k, v in params.items() if v is not None])


def import_filtering_job(job_id: str, input_dir: any, slurm_job_id: int = None):
    print(f"Importing filtering results from {input_dir}")
    results = import_filtering_results(input_dir)
    if not results:
        raise RuntimeError(f"Error importing filtering results for job {job_id}")

    erbench_client.send_results(job_id, JobStatus.MATCHING, results)
    print("Filtering results uploaded successfully")


def import_job(job_id: str, input_dir: any, slurm_job_id: int = None):
    print(f"Importing results from {input_dir}")

    slurm_job_str = None
    if slurm_job_id:
        try:
            print(f"Retrieving Slurm metrics for job {slurm_job_id}")
            process = subprocess.run(["sacct", "-j", str(slurm_job_id), "--json"], capture_output=True, text=True)
            if process.returncode == 0:
                slurm_job_str = process.stdout.replace("\n", "").strip()
            else:
                print(f"Warning: Failed to retrieve Slurm metrics: {process.stderr}")
        except Exception as e:
            print(f"Warning: Error retrieving Slurm metrics: {str(e)}")

    results = import_results(input_dir)
    if not results:
        raise RuntimeError(f"Error importing results for job {job_id}")

    if slurm_job_str:
        results = import_slurm_metrics(slurm_job_str, results)
        print("Slurm metrics retrieved successfully")

    erbench_client.send_results(job_id, JobStatus.COMPLETED, results)
    print("Results upload completed successfully")

    predictions = import_predictions(input_dir)
    if not predictions:
        raise RuntimeError(f"Error importing predictions for job {job_id}")

    erbench_client.send_predictions(job_id, predictions)
    print("Predictions upload completed successfully")


def send_email_notification(job_id: str, notify_email: str):
    try:
        msg = EmailMessage()
        msg.set_content(f"Your entity resolution job {job_id} has been completed.\n\nYou can view the results at {ERBENCH_URL}/jobs/{job_id}")
        msg["Subject"] = f"[{job_id}] SMBench Job Completed"
        msg["From"] = os.getenv("EMAIL_FROM")
        msg["To"] = notify_email
        msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

        smtp_server = os.getenv("SMTP_SERVER", "localhost")
        smtp_port = int(os.getenv("SMTP_PORT", 25))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if smtp_user and smtp_password:
                server.starttls()
                server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print(f"Email notification sent to {notify_email}")
    except Exception as e:
        print(f"Error sending email notification: {str(e)}")


def get_job_directory(job_id: str) -> str:
    return os.path.join(TEMP_DIR, job_id)


def start_job(job: Job):
    dataset_path = os.path.join(DATASETS_DIR, job["dataset"]["code"])
    if not os.path.exists(dataset_path):
        raise RuntimeError(f"Dataset directory {dataset_path} does not exist")

    filtering_container = os.path.join(CONTAINERS_DIR, f"{job['filteringAlgo']['code']}.sif")
    if not os.path.exists(filtering_container):
        raise RuntimeError(f"Error: Filtering algorithm container {filtering_container} does not exist, skipping job")

    matching_container = os.path.join(CONTAINERS_DIR, f"{job['matchingAlgo']['code']}.sif")
    if not os.path.exists(matching_container):
        raise RuntimeError(f"Error: Matching algorithm container {matching_container} does not exist, skipping job")

    try:
        job_dir = get_job_directory(job["id"])
        print(f"Creating job directory: {job_dir}")
        os.makedirs(job_dir, exist_ok=True)

        # print(f"Copying dataset files from {dataset_path} to {job_dir}")
        # for item in os.listdir(dataset_path):
        #     shutil.copy2(os.path.join(dataset_path, item), os.path.join(job_dir, item))

        filtering_params = job["filteringParams"]
        if is_embeddings_required(job["filteringAlgo"]["code"]):
            filtering_params["embeddings"] = EMBEDDINGS_DIR
        filtering_params_str = render_params(filtering_params)

        filtering_slurm_params = {
            "job-name": f"erbench_filtering_{job['id']}",
            "parsable": True,
            "gpus": "1" if is_gpu_required(job["filteringAlgo"]["code"]) else None,
            "output": os.path.join(job_dir, "filtering.out"),
            "error": os.path.join(job_dir, "filtering.err"),
            "wrap": f"apptainer run {filtering_container} {dataset_path} {job_dir} {filtering_params_str}",
        }
        filtering_cmd = f"sbatch {SLURM_JOB_ARGS} {render_params(filtering_slurm_params)}"
        print(f"Filtering command: {filtering_cmd}")

        print(f"Starting filtering job {job['filteringAlgo']['code']} with params: {filtering_params_str}")
        process = subprocess.run(filtering_cmd, shell=True, capture_output=True, text=True)
        if process.returncode != 0:
            raise RuntimeError(f"Error running filtering job: {process.stderr}")

        filtering_job_id = int(process.stdout.strip())
        print(f"Filtering job submitted with ID: {filtering_job_id}")

        matching_params = job["matchingParams"]
        if is_embeddings_required(job["matchingAlgo"]["code"]):
            matching_params["embeddings"] = EMBEDDINGS_DIR
        matching_params_str = render_params(matching_params)

        matching_slurm_params = {
            "job-name": f"erbench_matching_{job['id']}",
            "parsable": True,
            "gpus": "1" if is_gpu_required(job["matchingAlgo"]["code"]) else None,
            "output": os.path.join(job_dir, "matching.out"),
            "error": os.path.join(job_dir, "matching.err"),
            "dependency": f"afterok:{filtering_job_id}",
            "wrap": f"apptainer run {matching_container} {job_dir} {matching_params_str}",
        }
        matching_cmd = f"sbatch {SLURM_JOB_ARGS} {render_params(matching_slurm_params)}"
        print(f"Matching command: {matching_cmd}")

        print(f"Starting matching job {job['matchingAlgo']['code']} with params: {matching_params_str}")
        process = subprocess.run(matching_cmd, shell=True, capture_output=True, text=True)
        if process.returncode != 0:
            raise RuntimeError(f"Error running matching job: {process.stderr}")

        matching_job_id = int(process.stdout.strip())
        print(f"Matching job submitted with ID: {matching_job_id}")

        erbench_client.update_job(job["id"], JobStatus.QUEUED, filtering_job_id, matching_job_id)
        print(f"Job {job['id']} updated to QUEUED status with filtering job ID {filtering_job_id} and matching job ID {matching_job_id}")
    except Exception as e:
        print(f"Error executing job: {str(e)}")


def get_job_status(slurm_job_id) -> str:
    process = subprocess.run(["sacct", "-j", str(slurm_job_id), "--format=State", "--parsable2", "--noheader"], capture_output=True, text=True)
    if process.returncode != 0:
        raise RuntimeError(f"Error checking job status: {process.stderr}")
    return process.stdout.strip().split("\n")[0]


def cancel_job(slurm_job_id):
    print(f"Cancelling job {slurm_job_id}")
    process = subprocess.run(["scancel", str(slurm_job_id)], capture_output=True, text=True)
    if process.returncode != 0:
        raise RuntimeError(f"Error cancelling job: {process.stderr}")
    print(f"Job {slurm_job_id} cancelled")


def check_job(job: Job):
    try:
        job_dir = get_job_directory(job["id"])

        if job["status"] == JobStatus.QUEUED or job["status"] == JobStatus.FILTERING:
            filtering_status = get_job_status(job["filteringSlurmId"])
            print(f"Filtering status: {filtering_status}")

            if filtering_status == "RUNNING" or filtering_status == "COMPLETING":
                if job["status"] != JobStatus.FILTERING:
                    erbench_client.update_job(job["id"], JobStatus.FILTERING)
                return
            elif filtering_status == "COMPLETED":
                import_filtering_job(job["id"], job_dir, job["filteringSlurmId"])
            elif filtering_status == "FAILED":
                erbench_client.update_job(job["id"], JobStatus.FAILED)
                cancel_job(job["matchingSlurmId"])
                print(f"Job {job['id']} failed")
                return

        matching_status = get_job_status(job["matchingSlurmId"])
        print(f"Matching status: {matching_status}")

        if matching_status == "COMPLETED":
            print(f"Importing results for job {job['id']} from {job_dir}")
            import_job(job["id"], job_dir, job["matchingSlurmId"])

            if job["notifyEmail"] and len(job["notifyEmail"]) > 0:
                print(f"Sending email notification to {job['notifyEmail']}")
                send_email_notification(job["id"], job["notifyEmail"])

            # Clean up the job directory after successful import
            print(f"Cleaning up job directory: {job_dir}")
            try:
                shutil.rmtree(job_dir)
                print(f"Job directory {job_dir} removed successfully")
            except Exception as e:
                print(f"Warning: Failed to remove job directory: {str(e)}")
        elif matching_status == "FAILED":
            erbench_client.update_job(job["id"], JobStatus.FAILED)
            print(f"Job {job['id']} failed")
    except Exception as e:
        erbench_client.update_job(job["id"], JobStatus.FAILED)
        print(f"Error checking job status: {str(e)}")


def run_job():
    jobs = erbench_client.get_jobs()
    for job in jobs:
        try:
            if job["status"] == JobStatus.PENDING:
                print(f"Starting job {job['id']}")
                start_job(job)
            elif job["status"] == JobStatus.QUEUED or job["status"] == JobStatus.FILTERING or job["status"] == JobStatus.MATCHING:
                print(f"Checking job {job['id']}")
                check_job(job)
        except Exception as e:
            print(f"Error processing job {job['id']}: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SMBench Manager CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    import_parser = subparsers.add_parser("import", help="Import results into database")
    import_parser.add_argument("job_id", type=str, help="The job ID in the SMBench database")
    import_parser.add_argument("input_dir", type=pathtype.Path(readable=True), help="The input directory containing the results")
    import_parser.add_argument("-sj", "--slurm-job-id", type=int, default=None, help="Slurm job ID, used to gather utilization metrics")
    import_parser.set_defaults(func=import_job)

    run_parser = subparsers.add_parser("run", help="Run entity resolution tasks")
    run_parser.set_defaults(func=run_job)

    test_email = subparsers.add_parser("test-email", help="Send test email")
    test_email.add_argument("job_id", type=str, help="The job ID in the SMBench database")
    test_email.add_argument("notify_email", type=str, help="The email address to send the notification to")
    test_email.set_defaults(func=send_email_notification)

    args = parser.parse_args()
    if hasattr(args, "func"):
        arg_dict = vars(args).copy()
        arg_dict.pop("func")
        arg_dict.pop("command", None)
        args.func(**arg_dict)
    else:
        parser.print_help()
        exit(1)
