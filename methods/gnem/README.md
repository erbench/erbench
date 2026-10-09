# GNEM

https://github.com/ChenRunjin/GNEM

## How to use

You can directly execute the docker image as following:

```bash
docker run --rm -v .:/data gnem
```

This will assume that you have the input dataset in the current directory,
it will mount it as `/data` and will output the results in the `output` subdirectory.

You can override the input and output directories by providing them as arguments to the docker image:

```bash
docker run -v ../../datasets/d2_abt_buy:/data/input:ro -v ../../test:/data/output gnem /data/input /data/output
```

## Apptainer

```bash
mkdir -p ../../apptainer ../../output/gnem
APPTAINER_HOME="" apptainer build ../../apptainer/gnem.sif container.def
srun -p ampere --gpus=1 apptainer run ../../apptainer/gnem.sif ../../datasets/d2_abt_buy/ ../../output/gnem/

# to verify efficiency
seff $jobid

# dev mode with bind
srun -p ampere --gpus=1 apptainer run --bind ./:/srv ../../apptainer/gnem.sif ../../datasets/d2_abt_buy/ ../../output/gnem/
```
