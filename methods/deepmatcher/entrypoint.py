import sys
sys.path.append('fork-deepmatcher')

import argparse
import time
import os
import pathtype

import pandas as pd
import deepmatcher as dm
from transform import transform_input, transform_output

parser = argparse.ArgumentParser(description='Benchmark a dataset with a method')
parser.add_argument('input', type=pathtype.Path(readable=True), nargs='?', default='/data',
                    help='Input directory containing the dataset')
parser.add_argument('output', type=str, nargs='?',
                    help='Output directory to store the output')
parser.add_argument('--embeddings', type=pathtype.Path(readable=True), nargs='?', default='/workspace/embeddings',
                    help='The directory where embeddings are stored')
parser.add_argument('-e', '--epochs', type=int, nargs='?', default=5,
                    help='Number of epochs to train the model')
args = parser.parse_args()

if args.output is None:
    args.output = args.input

if '/' not in args.output:
    args.output = os.path.join(args.input, args.output)

os.makedirs(args.output, exist_ok=True)
if not os.path.isdir(args.output) or not os.access(args.output, os.W_OK):
    print("output folder does not exits or is not writable")
    exit(1)

print("Hi, I'm DeepMatcher entrypoint!")
print("Input taken from: ", args.input)
print("Input directory: ", os.listdir(args.input))
print("Output directory: ", os.listdir(args.output))

transform_input(args.input, args.output)

# Step 1. Convert input data into the format expected by the method
datasets = dm.data.process(path=args.output,
                           train="train.csv",
                           validation="valid.csv",
                           test="test.csv",
                           id_attr='id',
                           label_attr='label',
                           left_prefix='tableA_',
                           right_prefix='tableB_',
                           cache=None,
                           embeddings_cache_path=args.embeddings)

train, valid, test = datasets[0], datasets[1], datasets[2] if len(datasets) >= 3 else None

# Step 2. Run the method
model = dm.MatchingModel()

start_time = time.process_time()
_, results_per_epoch = model.run_train(train, valid, test, epochs=args.epochs)
train_time = time.process_time() - start_time

start_time = time.process_time()
predictions, stats = model.run_eval(test, return_stats=True, return_predictions=True)
eval_time = time.process_time() - start_time


# Step 3. Convert the output into a common format
test_data =  pd.read_csv(os.path.join(args.input, 'test.csv'), encoding_errors='replace')
transform_output(predictions,test_data, stats, results_per_epoch, train_time, eval_time, args.output)
print("Final output: ", os.listdir(args.output))

# Step 4. Clean Output
os.remove(os.path.join(args.output, 'train.csv'))
os.remove(os.path.join(args.output, 'valid.csv'))
os.remove(os.path.join(args.output, 'test.csv'))
