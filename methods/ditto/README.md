# DITTO

https://github.com/nishadi/ditto

entrypoint.py based on train_ditto.py and matcher.py

## How to use

You can directly execute the docker image as following:

```bash
docker run --rm -v .:/data ditto
```

This will assume that you have the input dataset in the current directory,
it will mount it as `/data` and will output the results in the `output` subdirectory.

You can override the input and output directories by providing them as arguments to the docker image:

```bash
docker run -v ../../datasets/d2_abt_buy:/data/input:ro -v ../../test:/data/output ditto /data/input /data/output
```

## Apptainer

```bash
mkdir -p ../../apptainer ../../output/ditto
APPTAINER_HOME="" apptainer build ../../apptainer/ditto.sif container.def
srun -p ampere --gpus=1 apptainer run ../../apptainer/ditto.sif ../../datasets/d2_abt_buy/ ../../output/ditto/

# dev mode with bind
srun -p ampere --gpus=1 apptainer run --bind ./:/srv ../../apptainer/ditto.sif ../../datasets/d2_abt_buy/ ../../output/ditto/
```

## Last error

```bash

```
## User Warning

```bash
/opt/conda/lib/python3.7/site-packages/spacy/pipeline/lemmatizer.py:187: UserWarning: [W108] The rule-based lemmatizer did not find POS annotation for the token 'CARBON'. Check that your pipeline includes components that assign token.pos, typically 'tagger'+'attribute_ruler' or 'morphologizer'.

/opt/conda/lib/python3.7/site-packages/torch/cuda/__init__.py:143: UserWarning: 
NVIDIA H100 NVL with CUDA capability sm_90 is not compatible with the current PyTorch installation.
The current PyTorch install supports CUDA capabilities sm_37 sm_50 sm_60 sm_61 sm_70 sm_75 sm_80 sm_86 compute_37.
If you want to use the NVIDIA H100 NVL GPU with PyTorch, please check the instructions at https://pytorch.org/get-started/locally/

  warnings.warn(incompatible_device_warn.format(device_name, capability, " ".join(arch_list), device_name))
```
