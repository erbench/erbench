# SMBench Task Manager

## Setup

1. Create an `.env` file in this directory with the following content:

```env
API_BASE_URL=https://api.example.com

DATASETS_DIR=/abolute-path/datasets
CONTAINERS_DIR=/abolute-path/apptainer
EMBEDDINGS_DIR=/abolute-path/embeddings
TEMP_DIR=/abolute-path/running_jobs

SLURM_JOB_ARGS="--partition=whatever"
```

2. Install environment:

```bash
conda create -n erbench -f conda-env.yml
conda activate erbench
```

3. Run the manager:

```bash
python main.py run
```

This can be run as a cronjob, just make sure to use absolute paths.
