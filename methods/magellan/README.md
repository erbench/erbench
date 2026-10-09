# Magellan

https://github.com/anhaidgroup/py_entitymatching
https://github.com/nishadi/py_entitymatching_sample

The docker image should be self-contained and should be able to run the method without any additional user input.
The image should contain the source code of the method and input + output transformers.

!> This method does not use GPU acceleration.

## Structure

- [Dockerfile](Dockerfile) should contain the instructions to build the docker image.
- [transform.py](transform.py) contains pre-processing and post-processing functions that will be applied to the input and output data.
- [entrypoint.py](entrypoint.py) should contain the main method that will be executed inside the docker container.

## How to use

### Docker

You can directly execute the docker image as following:

```bash
docker run --rm -v .:/data magellan
```

This will assume that you have the input dataset in the current directory,
it will mount it as `/data` and will output the results in the `output` subdirectory.

You can override the input and output directories by providing them as arguments to the docker image:

```bash
docker run -v ../../datasets/d2_abt_buy:/data/input:ro -v ../../test:/data/output magellan /data/input /data/output
```

### Apptainer

```bash
mkdir -p ../../apptainer ../../output/magellan
APPTAINER_HOME="" apptainer build ../../apptainer/magellan.sif container.def
srun -p ampere apptainer run ../../apptainer/magellan.sif ../../datasets/d2_abt_buy/ ../../output/magellan/

# dev mode with bind
srun -p ampere apptainer run --bind ./:/srv ../../apptainer/magellan.sif ../../datasets/d2_abt_buy/ ../../output/magellan/
```
