# DeepMatcher

https://github.com/anhaidgroup/deepmatcher

## How to use

IMPORTANT! `/workspace/embedding` should be mounted with `wiki.en.bin` embeddings inside.

You can directly execute the docker image as following:

```bash
docker run --rm -v .:/data deepmatcher
```

This will assume that you have the input dataset in the current directory,
it will mount it as `/data` and will output the results in the `output` subdirectory.

You can override the input and output directories by providing them as arguments to the docker image:

```bash
docker run -v ../../datasets/d2_abt_buy:/data/input:ro -v ../../test:/data/output -v ../../embedding:/workspace/embedding deepmatcher /data/input /data/output
```

## Apptainer

```bash
mkdir -p ../../apptainer ../../output/deepmatcher
apptainer build ../../apptainer/deepmatcher.sif container.def
srun --gpus=1 apptainer run ../../apptainer/deepmatcher.sif ../../datasets/d2_abt_buy/ ../../output/deepmatcher/ ../../embedding/

# to verify efficiency
seff $jobid

# dev mode with bind
srun --gpus=1 apptainer run --bind ./:/srv ../../apptainer/deepmatcher.sif ../../datasets/d2_abt_buy/ ../../output/deepmatcher/ ../../embedding/
```
