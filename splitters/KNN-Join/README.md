# KNN-Join dataset splitter

Splits the dataset into training, validation, and testing sets.
Based on [KNN-Join](https://pyjedai.readthedocs.io/en/latest/tutorials/SimilarityJoins.html).

## Expected directory structure

It is expected that it contains the following files (in proper CSV format):

- `tableA.csv` where the first row is the header, and it has to contain the `id` attribute
- `tableB.csv` same as `tableA.csv`
- `matches.csv` should have `tableA_id`, `tableB_id` attributes, which means that the `tableA_id` record is a match with the `tableB_id` record

The produced output will include two files, and the split by recall value provided (0.7 by default):

- `test.csv` where attributes are: `tableA_id`, `tableB_id` and `label` (0 or 1). The label is 1 if the pair is a match, 0 otherwise
- `train.csv` same as `test.csv`

## Apptainer

```bash
mkdir -p ../../apptainer ../../output
apptainer build ../../apptainer/splitter_knnjoin.sif container.def
srun --gpus=0 -p ampere apptainer run ../../apptainer/splitter_knnjoin.sif ../../datasets/d2_abt_buy/ kj_split

# dev mode with bind
srun --gpus=0 -p ampere apptainer run --bind ./:/srv ../../apptainer/splitter_knnjoin.sif ../../datasets/d2_abt_buy/ kj_split
```
