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
