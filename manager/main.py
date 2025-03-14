import argparse
import pathtype

from erbench.client import ErbenchClient, JobStatus
from erbench.importer import import_results
from manager.erbench.importer import import_predictions

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Imports results of entity resolution tasks into database')
    parser.add_argument('job_id', type=str,
                        help='The job ID of the entity resolution task to be imported')
    parser.add_argument('input_dir', type=pathtype.Path(readable=True),
                        help='The input directory containing the results of the entity resolution task')
    parser.add_argument('-sj', '--slurm-job-id', type=int, nargs='?', default=None,
                        help='Slurm job ID of the entity resolution task, used to gather utilization metrics')
    args = parser.parse_args()

    print(f"Importing results for job {args.job_id} from {args.input_dir}")

    # Initialize the client (loads configuration from .env file)
    erbench_client = ErbenchClient()

    results = import_results(args.input_dir)
    if not results: exit(1)

    erbench_client.send_results(args.job_id, JobStatus.COMPLETED, results)
    print("Results upload completed successfully")

    predictions = import_predictions(args.input_dir)
    if not predictions: exit(1)

    erbench_client.send_predictions(args.job_id, predictions)
    print("Predictions upload completed successfully")

    exit(0)
