# No-code Benchmarking of Entity Resolution

https://swimlanes.io/u/k3Rmy375P

The main requirement is to implement the following process:

- to set several DL-based matching algorithms running on a server as Docker containers
- to feed one of them with three sets of record pairs from pyJedAI' blocking (training, validation and testing)
- to receive the labels of the pairs in the testing set

## Repository setup

```bash
git clone git@github.com:erbench/erbench.git
git submodule update --recursive --init
```

### Download embeddings

```bash
mkdir embedding
wget https://zenodo.org/record/6466387/files/wiki.en.bin -O embedding/wiki.en.bin
```

## Methods

### Splitters

| Name                                             | Container  |
|--------------------------------------------------|------------|
| [Random Split](splitters/random-split/README.md) | ok, no GPU |
| [DeepBlocker](splitters/DeepBlocker/README.md)   | ok         |
| [KNN-Join](splitters/KNN-Join/README.md)         | ?          |

### Matchers

| Name                                             | Container  | Input params (exposed to UI)               | Metrics columns                                         | Predictions columns                      |
|--------------------------------------------------|------------|--------------------------------------------|---------------------------------------------------------|------------------------------------------|
| [deepmatcher](methods/deepmatcher/README.md)     | ok         | input, output, embedding, --epochs         | f1, precision, recall, train_time, eval_time            | tableA_id, tableB_id, label, prob_class1 |
| [ditto](methods/ditto/README.md)                 | ok         | input, output, --epochs, --seed            | f1, precision, recall, train_time, eval_time            | tableA_id, tableB_id, label, prob_class1 |
| [emtransformer](methods/emtransformer/README.md) | ok         | input, output, --epochs, --seed            | f1, precision, recall, train_time, eval_time            | tableA_id, tableB_id, label, prob_class1 |
| [gnem](methods/gnem/README.md)                   | ok         | input,output,--epochs                      | f1, precision, recall, train_time, eval_time            | tableA_id, tableB_id, label, prob_class1 |
| [hiermatcher](methods/hiermatcher/README.md)     | ok         | input, output, embedding, --epochs, --seed | f1, precision, recall, train_time, eval_time            | tableA_id, tableB_id, label, prob_class1 |
| [magellan](methods/magellan/README.md)           | ok, no GPU | input, output, --method, --seed            | f1, precision, recall, train_time, eval_time            | tableA_id, tableB_id, label, prob_class1 |
| [zeroer](methods/zeroer/README.md)               | ok, no GPU | input, output, --full                      | f1, precision, recall, train_time (always 0), eval_time | tableA_id, tableB_id, label, prob_class1 |
