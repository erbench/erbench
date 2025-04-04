import sys
sys.path.append('fork-gnem')

import argparse
import pathtype
import pandas as pd

from transform import transform_output
import time
import os
from train_GNEM import train
import torch
from transformers import AdamW, get_linear_schedule_with_warmup
from dataset import MatchingDataset, collate_fn, MergedMatchingDataset
from torch.utils.data import DataLoader
from EmbedModel import EmbedModel
from GCN import gcn
from logger import set_logger
from torch.utils.tensorboard import SummaryWriter
import torch.nn as nn
import random
import numpy as np

parser = argparse.ArgumentParser(description='Benchmark a dataset with a method')
parser.add_argument('input', type=pathtype.Path(readable=True), nargs='?', default='/data',
                    help='Input directory containing the dataset')
parser.add_argument('output', type=str, nargs='?',
                    help='Output directory to store the output')
parser.add_argument('-e', '--epochs', type=int, nargs='?', default=1,
                    help='Number of epochs to train the model')
parser.add_argument('-s', '--seed', type=int, nargs='?', default=random.randint(0, 4294967295),
                    help='The random state used to initialize the algorithms and split dataset')
args = parser.parse_args()

if args.output is None:
    args.output = args.input

os.makedirs(args.output, exist_ok=True)
if not os.path.isdir(args.output) or not os.access(args.output, os.W_OK):
    print("output folder does not exits or is not writable")
    exit(1)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
torch.manual_seed(args.seed)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(args.seed)
np.random.seed(args.seed)

print("Hi, I'm GNEM entrypoint!")
print("Input taken from: ", args.input)
print("Input directory: ", os.listdir(args.input))
print("Output directory: ", os.listdir(args.output))

train_table = pd.read_csv(os.path.join(args.input, 'train.csv'), encoding_errors='replace')
val_table = pd.read_csv(os.path.join(args.input, 'valid.csv'), encoding_errors='replace')
test_table = pd.read_csv(os.path.join(args.input, 'test.csv'), encoding_errors='replace')

train_table = train_table.loc[:,['tableA_id', 'tableB_id', 'label']]
print(train_table)
train_table.columns = ['ltable_id', 'rtable_id', 'label']
val_table = val_table.loc[:,['tableA_id', 'tableB_id', 'label']]
val_table.columns = ['ltable_id', 'rtable_id', 'label']
test_table = test_table.loc[:,['tableA_id', 'tableB_id', 'label']]
test_table.columns = ['ltable_id', 'rtable_id', 'label']
train_table.to_csv(os.path.join(args.output, 'train.csv'), index=False)
val_table.to_csv(os.path.join(args.output, 'valid.csv'), index=False)
test_table.to_csv(os.path.join(args.output, 'test.csv'), index=False)

tableA = pd.read_csv(os.path.join(args.input, 'tableA.csv'), encoding_errors='replace')
str_cols = [col for col in tableA.columns if col != 'id']
tableA[str_cols] = tableA[str_cols].astype(str)
tableB = pd.read_csv(os.path.join(args.input, 'tableB.csv'), encoding_errors='replace')
str_cols = [col for col in tableB.columns if col != 'id']
tableB[str_cols] = tableB[str_cols].astype(str)


useful_field_num = len(tableA.columns)-1
gcn_dim = 768

val_dataset = MergedMatchingDataset(os.path.join(args.output, 'valid.csv'), tableA, tableB,
                                    other_path=[os.path.join(args.output, 'train.csv'), os.path.join(args.output, 'test.csv')])
test_dataset = MergedMatchingDataset(os.path.join(args.output, 'test.csv'), tableA, tableB,
                                     other_path=[os.path.join(args.output, 'train.csv'), os.path.join(args.output, 'valid.csv')])
train_dataset = MatchingDataset(os.path.join(args.output, 'train.csv'), tableA, tableB)

batch_size = 2
train_iter = DataLoader(train_dataset, batch_size=batch_size, collate_fn=collate_fn, shuffle=True)
val_iter = DataLoader(val_dataset, batch_size=batch_size, collate_fn=collate_fn, shuffle=False)
test_iter = DataLoader(test_dataset, batch_size=batch_size, collate_fn=collate_fn, shuffle=False)

embedmodel = EmbedModel(useful_field_num=useful_field_num, lm = 'bert', device=device)

gcn_layer = 1
dropout = 0.0
model = gcn(dims=[gcn_dim]*(gcn_layer + 1),  dropout=dropout)

no_decay = ['bias', 'LayerNorm.weight']
weight_decay = 0.0
embed_lr = 0.00002
lr = 0.0001

optimizer_grouped_parameters = [
    {'params': [p for n, p in embedmodel.named_parameters() if not any(nd in n for nd in no_decay)],
     'weight_decay': weight_decay, 'lr': embed_lr},
    {'params': [p for n, p in embedmodel.named_parameters() if any(nd in n for nd in no_decay)],
     'weight_decay': 0.0, 'lr': embed_lr},
    {'params': [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)],
     'weight_decay': weight_decay, 'lr': lr},
    {'params': [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)],
     'weight_decay': 0.0, 'lr': lr}
]

num_train_steps = len(train_iter) * args.epochs
opt = AdamW(optimizer_grouped_parameters, eps=1e-8)
scheduler = get_linear_schedule_with_warmup(opt, num_warmup_steps=0, num_training_steps=num_train_steps)

log_dir = os.path.join(args.output, "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logger = set_logger(os.path.join(log_dir, str(time.time()) + ".log"))
tf_logger = SummaryWriter(log_dir)

start_epoch = 0
start_f1 = 0.0

pos_neg_ratio = 1.0

embedmodel = embedmodel.to(embedmodel.device)
model = model.to(embedmodel.device)
pos = 2.0 * pos_neg_ratio / (1.0 + pos_neg_ratio)
neg = 2.0 / (1.0 + pos_neg_ratio)
criterion = nn.CrossEntropyLoss(weight=torch.Tensor([neg, pos])).to(embedmodel.device)
log_freq = len(train_iter)//10

start_time = time.process_time()
f1s, ps, rs, score_dicts, time_m, res_per_epoch = train(train_iter, args.output, logger, tf_logger, model, embedmodel, opt, criterion, args.epochs, test_iter=test_iter, val_iter=val_iter,
      scheduler=scheduler, log_freq=log_freq, start_epoch=start_epoch, start_f1=start_f1, score_type=['mean'])
eval_time = time.process_time() - time_m
train_time =  time_m - start_time

transform_output(score_dicts, f1s, ps, rs, train_time, eval_time, res_per_epoch, args.output)
print("Final output: ", os.listdir(args.output))
