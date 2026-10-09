# ZeroER

https://github.com/nishadi/zeroer
entrypoint.py based on zeroer.py

!> This method does not use GPU acceleration.

## How to use

```bash
conda create -n zeroer python=3.7
conda activate zeroer
pip install -r requirements.txt -r fork-zeroer/requirements.txt
python -u entrypoint.py ../../datasets/d2_abt_buy/ ../../output/zeroer/
```

### Docker

You can directly execute the docker image as following:

```bash
docker run --rm -v .:/data zeroer
```

This will assume that you have the input dataset in the current directory,
it will mount it as `/data` and will output the results in the `output` subdirectory.

You can override the input and output directories by providing them as arguments to the docker image:

```bash
docker run -v ../../datasets/d2_abt_buy:/data/input:ro -v ../../test:/data/output zeroer /data/input /data/output
```

### Apptainer

```bash
mkdir -p ../../apptainer ../../output/zeroer
APPTAINER_HOME="" apptainer build ../../apptainer/zeroer.sif container.def
srun -p ampere apptainer run ../../apptainer/zeroer.sif ../../datasets/d2_abt_buy/ ../../output/zeroer/

# dev mode with bind
srun -p ampere apptainer run --bind ./:/srv ../../apptainer/zeroer.sif ../../datasets/d2_abt_buy/ ../../output/zeroer/
```
