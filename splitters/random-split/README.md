# Simple Dataset Splitter (a.k.a. random splitter)

Splits the dataset into training, validation, and testing sets.

## Expected directory structure

It is expected that it contains the following files (in proper CSV format):

- `tableA.csv` where the first row is the header, and it has to contain the `id` attribute
- `tableB.csv` same as `tableA.csv`
- `matches.csv` should have `tableA_id`, `tableB_id` attributes, which means that the `tableA_id` record is a match with the `tableB_id` record

The produced output will include the following files:

- `test.csv` where attributes are: `tableA_attr` for all attributes attr (incl. id) from table A; `tableB_attr` for all attributes attr (incl. id) from table B and `label` (0 or 1). The label is 1 if the pair is a match, 0 otherwise
- `train.csv` same as `test.csv`
- `valid.csv` same as `test.csv`
- `tableA.csv`, `tableB.csv` and `matches.csv` will be copied to the output folder.
- `split_statistics.txt`: Recall, Precision and size of the produced candidates and the splits.

# How to use

## Apptainer

```bash
mkdir -p ../../apptainer ../../output
apptainer build ../../apptainer/splitter_simple.sif container.def
srun --gpus=0 -p ampere apptainer run ../../apptainer/splitter_simple.sif ../../datasets/d2_abt_buy/ r_split

# dev mode with bind
srun --gpus=0 -p ampere apptainer run --bind ./:/srv ../../apptainer/splitter_simple.sif ../../datasets/d2_abt_buy/ r_split
```
