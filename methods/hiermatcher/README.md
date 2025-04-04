# HierMatcher

https://github.com/nishadi/EntityMatcher

## How to use

IMPORTANT! `/workspace/embeddings` should be mounted with `wiki.en.bin` embeddings inside.

You can directly execute the docker image as following:

```bash
docker run --rm -v .:/data hiermatcher
```

This will assume that you have the input dataset in the current directory,
it will mount it as `/data` and will output the results in the `output` subdirectory.

You can override the input and output directories by providing them as arguments to the docker image:

```bash
docker run -v ../../datasets/d2_abt_buy:/data/input:ro -v ../../test:/data/output -v ../../embeddings:/workspace/embeddings hiermatcher /data/input /data/output
```

## Apptainer

```bash
mkdir -p ../../apptainer ../../output/hiermatcher
apptainer build ../../apptainer/hiermatcher.sif container.def
srun -p ampere --gpus=1 apptainer run ../../apptainer/hiermatcher.sif ../../datasets/d2_abt_buy/ ../../output/hiermatcher/ --embeddings ../../embeddings/

# dev mode with bind
srun -p ampere --gpus=1 apptainer run --bind ./:/srv ../../apptainer/hiermatcher.sif ../../datasets/d2_abt_buy/ ../../output/hiermatcher/ --embeddings ../../embeddings/
```
