import sys
sys.path.append('fork-zeroer')

import argparse
import pathtype
import os

import py_entitymatching as em
from transform import transform_input, transform_output
from data_loading_helper.feature_extraction import gather_features_and_labels, gather_similarity_features
import numpy as np
import utils
import time

def add_catalog_information(df, tableA, tableB):
    em.set_ltable(df, tableA)
    em.set_rtable(df, tableB)
    em.set_fk_ltable(df, 'ltable_id')
    em.set_fk_rtable(df, 'rtable_id')
    em.set_key(df, '_id')

parser = argparse.ArgumentParser(description='Benchmark a dataset with a method')
parser.add_argument('input', type=pathtype.Path(readable=True), nargs='?', default='/data',
                    help='Input directory containing the dataset')
parser.add_argument('output', type=str, nargs='?',
                    help='Output directory to store the output')
parser.add_argument('-f', '--full', action='store_true',
                    help='To perform matching on the full dataset or only on the test set')
args = parser.parse_args()

if args.output is None:
    args.output = args.input

os.makedirs(args.output, exist_ok=True)
if not os.path.isdir(args.output) or not os.access(args.output, os.W_OK):
    print("output folder does not exits or is not writable")
    exit(1)

print("Hi, I'm ZeroER entrypoint!")
print("Input taken from: ", args.input)
print("Input directory: ", os.listdir(args.input))
print("Output directory: ", os.listdir(args.output))

if args.full:
    print('Running ZeroER on full dataset')
else:
    print('Running ZeroER on test dataset')

excl_attributes = ['_id', 'ltable_id', 'rtable_id', 'label']


    
read_prefixes = ['tableA_', 'tableB_']
t_input = time.perf_counter()
dataset, tableA, tableB, GT = transform_input(args.input, read_prefixes, args.full)
print(f'Input reading done after {time.perf_counter() - t_input:.4f}s')

prep_time = time.perf_counter()
em.set_key(tableA, 'id')
em.set_key(tableB, 'id')
add_catalog_information(dataset, tableA, tableB)

id_df = dataset[["ltable_id", "rtable_id"]]
cand_features = gather_features_and_labels(tableA, tableB, GT, dataset)
sim_features = gather_similarity_features(cand_features)
prep_time = time.perf_counter() - prep_time

print(f'preprocessing done after {prep_time:.4f}s')

sim_features_lr = (None,None)
id_dfs = (id_df, None, None)

true_labels = cand_features.gold.values
if np.sum(true_labels)==0:
    true_labels = None

start_time = time.perf_counter()
y_pred, results_per_iteration, model = utils.run_zeroer(sim_features, sim_features_lr,id_dfs,
                    true_labels , LR_dup_free= True, LR_identical=False, run_trans=True)
train_time = time.perf_counter() - start_time
print(f"Evaluation done after {train_time:.4f}s")

start_time = time.perf_counter()
y_pred = model.predict_PM(sim_features.values)

ids = id_df.values
id_tuple_to_index = dict([])
for i in range(ids.shape[0]):
    id_tuple_to_index[(ids[i,0],ids[i,1])] = i
    id_tuple_to_index[(ids[i,1], ids[i,0])] = i
y_pred = model.enforce_transitivity(y_pred, ids, id_tuple_to_index, None, None, LR_dup_free=True, LR_identical=False)
eval_time = time.perf_counter() - start_time


pred_df = cand_features.copy()
pred_df['pred'] = y_pred

transform_output(pred_df, results_per_iteration, train_time, eval_time, prep_time, args.output)
