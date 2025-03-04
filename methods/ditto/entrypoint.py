import sys
sys.path.append('fork-ditto')

import os
import pathtype
import argparse
import random
import sys
import torch
import numpy as np
from collections import namedtuple
import time

from transform import transform_input, transform_output

sys.path.insert(0, "Snippext_public")

from ditto_light.dataset import DittoDataset
from ditto_light.summarize import Summarizer
from ditto_light.knowledge import ProductDKInjector, GeneralDKInjector
from ditto_light.ditto import train
from matcher import classify, tune_threshold

from scipy.special import softmax


parser = argparse.ArgumentParser(description='Benchmark a dataset with a method')
parser.add_argument('input', type=pathtype.Path(readable=True), nargs='?', default='/data',
                    help='Input directory containing the dataset')
parser.add_argument('output', type=str, nargs='?', default='/data/output',
                    help='Output directory to store the output')
parser.add_argument('-s', '--seed', type=int, nargs='?', default=random.randint(0, 4294967295),
                    help='The random state used to initialize the algorithms and split dataset')
parser.add_argument('-e', '--epochs', type=int, nargs='?', default=10,
                    help='Number of epochs to train the model')
parser.add_argument('-lm', '--languagemodel', type=str, nargs='?', default='RoBERTa',
                    help='The language model to use', choices=['RoBERTa', 'DistilBERT'])

args = parser.parse_args()

os.makedirs(args.output, exist_ok=True)
temp_output = os.path.join(args.output, 'temp')
os.makedirs(temp_output, exist_ok=True)

print("Hi, I'm DITTO entrypoint!")
print("Input taken from: ", args.input)
print("Input directory: ", os.listdir(args.input))
print("Output directory: ", os.listdir(args.output))

# Step 1. Convert input data into the format expected by the method
print("Method input: ", os.listdir(args.input))
prefix_1 = 'tableA_'
prefix_2 = 'tableB_'
trainset, validset, testset, train_ids, valid_ids, test_ids = transform_input(args.input, temp_output, prefixes=[prefix_1, prefix_2])

hyperparameters = namedtuple('hyperparameters', ['lm', #language Model
                                                 'n_epochs', #number of epochs
                                                 'batch_size',
                                                 'max_len', #max number of tokens as input for language model
                                                 'lr', #learning rate
                                                 'save_model',
                                                 'logdir',
                                                 'fp16', #train with half precision
                                                 'da', #data augmentation
                                                 'alpha_aug',
                                                 'dk', #domain knowledge
                                                 'summarize', #summarize to max_len
                                                 'size',#dataset size
                                                 'run_id'])

hp = hyperparameters(lm = args.languagemodel.lower(),
                     n_epochs = args.epochs,
                     batch_size = 64,
                     max_len = 256,
                     lr = 3e-5,
                     save_model = False,
                     logdir = temp_output,
                     fp16 = True,
                     da = 'all',
                     alpha_aug = 0.8,
                     dk = 'general',
                     summarize = True,
                     size = None,
                     run_id = 0)




#parser.add_argument("--finetuning", dest="finetuning", action="store_true")

# set seeds
seed = args.seed
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(seed)

# only a single task for baseline
task = args.input

# create the tag of the run
run_tag = '%s_lm=%s_da=%s_dk=%s_su=%s_size=%s_id=%d' % (task, hp.lm, hp.da,
        hp.dk, hp.summarize, str(hp.size), hp.run_id)
run_tag = run_tag.replace('/', '_')

# # load task configuration
# configs = json.load(open('configs.json'))
# configs = {conf['name'] : conf for conf in configs}
# config = configs[task]

# trainset = config['trainset']
# #validset = config['validset']
# testset = config['testset']

config = {"task_type": "classification",
  "vocab": ["0", "1"],
  "trainset": os.path.join(temp_output, 'train.txt'),
  "validset":os.path.join(temp_output, 'valid.txt'),
  "testset": os.path.join(temp_output, 'test.txt')}

# summarize the sequences up to the max sequence length
if hp.summarize:
    summarizer = Summarizer(config, lm=hp.lm)
    trainset = summarizer.transform_file(trainset, max_len=hp.max_len)
    validset = summarizer.transform_file(validset, max_len=hp.max_len)
    testset = summarizer.transform_file(testset, max_len=hp.max_len)

if hp.dk is not None:
    if hp.dk == 'product':
        injector = ProductDKInjector(config, hp.dk)
    else:
        injector = GeneralDKInjector(config, hp.dk)

    trainset = injector.transform_file(trainset)
    validset = injector.transform_file(validset)
    testset = injector.transform_file(testset)

# load train/dev/test sets
train_dataset = DittoDataset(trainset,
                               lm=hp.lm,
                               max_len=hp.max_len,
                               size=hp.size,
                               da=hp.da)
valid_dataset = DittoDataset(validset, lm=hp.lm)
test_dataset = DittoDataset(testset, lm=hp.lm)

# train and evaluate the model
start_time = time.process_time()
matcher, threshold, results_per_epoch = train(train_dataset,valid_dataset, test_dataset, run_tag, hp)
train_time = time.process_time() - start_time

pairs = []
#threshold = 0.5

# batch processing
out_data = []
start_time = time.process_time()
predictions, logits, labels = classify(testset, matcher, lm=hp.lm,
                               batch_size = hp.batch_size,
                               max_len=hp.max_len,
                               threshold=threshold)
scores = softmax(logits, axis=1)
eval_time = time.process_time() - start_time

transform_output(scores, threshold, results_per_epoch, test_ids, labels, train_time, eval_time, args.output)

# Step 4. Delete temporary files
for file in os.listdir(temp_output):
    if os.path.isfile(os.path.join(temp_output, file)):
        os.remove(os.path.join(temp_output, file))
