import sys
sys.path.append('fork-deepmatcher')

import argparse
import time
import os
import pathtype

import pandas as pd
import deepmatcher as dm
from HierMatcher import *
from transform import transform_input, transform_output

parser = argparse.ArgumentParser(description='Benchmark a dataset with a method')
parser.add_argument('input', type=pathtype.Path(readable=True), nargs='?', default='/data',
                    help='Input directory containing the dataset')
parser.add_argument('output', type=str, nargs='?', default='/data/output',
                    help='Output directory to store the output')
parser.add_argument('embedding', type=pathtype.Path(readable=True), nargs='?', default='/workspace/embedding',
                    help='The directory where embeddings are stored')
parser.add_argument('-s', '--seed', type=int, nargs='?', default=random.randint(0, 4294967295),
                    help='The random state used to initialize the algorithms and split dataset')
parser.add_argument('-e', '--epochs', type=int, nargs='?', default=1,
                    help='Number of epochs to train the model')

args = parser.parse_args()
os.makedirs(args.output, exist_ok=True)

print("Hi, I'm HierMatcher entrypoint!")
print("Input taken from: ", args.input)
print("Input directory: ", os.listdir(args.input))
print("Output directory: ", os.listdir(args.output))

transform_input(args.input, args.output)

# Step 1. Convert input data into the format expected by the method
datasets = dm.data.process(path=args.output,
                           train="train.csv",
                           validation='valid.csv',
                           test="test.csv",
                           id_attr='id',
                           label_attr='label',
                           left_prefix='tableA_',
                           right_prefix='tableB_',
                           cache=None,
                           embeddings_cache_path=args.embedding)

train, valid, test = datasets[0], datasets[1], datasets[2] if len(datasets) >= 3 else None

# Step 2. Run the method
model = HierMatcher(hidden_size=150, embedding_length=300, manualSeed=args.seed)

start_time = time.process_time()
_, results_per_epoch = model.run_train(train, valid, test, epochs=args.epochs, batch_size=32, label_smoothing=0.05, pos_weight=1.5)
train_time = time.process_time() - start_time

start_time = time.process_time()
predictions, stats = model.run_eval(test, return_stats=True, return_predictions=True)
eval_time = time.process_time() - start_time

# Step 3. Convert the output into a common format
test_data =  pd.read_csv(os.path.join(args.input, 'test.csv'), encoding_errors='replace')
transform_output(predictions, test_data, stats, results_per_epoch, train_time, eval_time, args.output)

# Step 4. Clean Output
os.remove(os.path.join(args.output, 'train.csv'))
os.remove(os.path.join(args.output, 'valid.csv'))
os.remove(os.path.join(args.output, 'test.csv'))

print("Final output: ", os.listdir(args.output))
