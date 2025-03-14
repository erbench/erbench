import argparse
import pathtype

from erbench.client import ErbenchClient
from erbench.importer import import_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Imports results of entity resolution tasks into database')
    parser.add_argument('job_id', type=str,
                        help='The job ID of the entity resolution task to be imported')
    parser.add_argument('input_dir', type=pathtype.Path(readable=True),
                        help='The input directory containing the results of the entity resolution task')
    parser.add_argument('-sj', '--slurm-job-id', type=int, nargs='?', default=None,
                        help='Slurm job ID of the entity resolution task, used to gather utilization metrics')
    args = parser.parse_args()

    # Initialize the client (loads configuration from .env file)
    erbench_client = ErbenchClient()

    print(f"Importing results for job {args.job_id} from {args.input_dir}")
    if import_results(args.job_id, args.input_dir, erbench_client):
        print(f"Data population complete for job {args.job_id}")
    else:
        exit(1)

    print("Data upload completed successfully")
    exit(0)
