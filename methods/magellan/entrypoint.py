import os
import argparse
import time
import random

import pathtype
import pandas as pd
import numpy as np
import py_entitymatching as em
from transform import transform_output
from sklearn.preprocessing import StandardScaler

parser = argparse.ArgumentParser(description='Benchmark a dataset with a method')
parser.add_argument('input', type=pathtype.Path(readable=True), nargs='?', default='/data',
                    help='Input directory containing the dataset')
parser.add_argument('output', type=str, nargs='?',
                    help='Output directory to store the output')
parser.add_argument('-m', '--method', type=str, default="RF",
                    choices=["DecisionTree", "SVM", "RF", "LogReg", "LinReg", "NaiveBayes"],
                    help='Method to use for the algorithm')
parser.add_argument('-s', '--seed', type=int, nargs='?', default=random.randint(0, 4294967295),
                    help='The random state used to initialize the algorithms and split dataset')
args = parser.parse_args()

if args.output is None:
    args.output = args.input

os.makedirs(args.output, exist_ok=True)
if not os.path.isdir(args.output) or not os.access(args.output, os.W_OK):
    print("output folder does not exits or is not writable")
    exit(1)

print("Hi, I'm Magellan entrypoint!")
print("Input taken from: ", args.input)
print("Input directory: ", os.listdir(args.input))
print("Output directory: ", os.listdir(args.output))

excl_attributes = ['tableA_id', 'tableB_id', 'label', 'id']
def add_catalog_information(df, tableA, tableB):
    em.set_ltable(df, tableA)
    em.set_rtable(df, tableB)
    em.set_fk_ltable(df, 'tableA_id')
    em.set_fk_rtable(df, 'tableB_id')
    em.set_key(df, 'id')


# Step 1. Convert input data into the format expected by the method
print("Method input: ", os.listdir(args.input))
tableA = pd.read_csv(os.path.join(args.input, 'tableA.csv'), encoding_errors='replace')
tableB = pd.read_csv(os.path.join(args.input, 'tableB.csv'), encoding_errors='replace')
train = pd.read_csv(os.path.join(args.input, 'train.csv'), encoding_errors='replace')
test = pd.read_csv(os.path.join(args.input, 'test.csv'), encoding_errors='replace')

tableA.rename(columns=lambda x: x.split('/')[-1], inplace=True)
tableB.rename(columns=lambda x: x.split('/')[-1], inplace=True)
train.rename(columns=lambda x: x.split('/')[-1], inplace=True)
test.rename(columns=lambda x: x.split('/')[-1], inplace=True)

train['id'] = np.arange(train.shape[0])
test['id'] = np.arange(test.shape[0])

em.set_key(tableA, 'id')
em.set_key(tableB, 'id')

add_catalog_information(train, tableA, tableB)
add_catalog_information(test, tableA, tableB)

# Step 2. Run the method
# https://nbviewer.org/github/anhaidgroup/py_entitymatching/blob/master/notebooks/guides/step_wise_em_guides/Selecting%20the%20Best%20Learning%20Matcher.ipynb

if args.method == "DecisionTree":
    matcher = em.DTMatcher(name='DecisionTree', random_state=args.seed)
elif args.method == "SVM":
    matcher = em.SVMMatcher(name='SVM', random_state=args.seed)
elif args.method == "RF":
    matcher = em.RFMatcher(name='RF', random_state=args.seed)
elif args.method == "LogReg":
    matcher = em.LogRegMatcher(name='LogReg', random_state=args.seed)
elif args.method == "LinReg":
    matcher = em.LinRegMatcher(name='LinReg')
elif args.method == "NaiveBayes":
    matcher = em.NBMatcher(name='NaiveBayes')
else:
    raise ValueError("Invalid method")

# get features and remove those containing the id attribute
F = em.get_features_for_matching(tableA, tableB, validate_inferred_attr_types=False)
for num, feature in enumerate(F.feature_name):
    if 'id' not in feature:
        break
F = F[num:]

# get feature vectors for the train and test set
train_f_vectors = em.extract_feature_vecs(train, feature_table=F, attrs_after='label')
test_f_vectors = em.extract_feature_vecs(test, feature_table=F, attrs_after='label')

# remove NaN values from the feature vectors by replacing them with the mean
if not pd.notnull(train_f_vectors).to_numpy().all():
    train_f_vectors = em.impute_table(train_f_vectors, missing_val=np.nan, exclude_attrs=excl_attributes, strategy='mean')

# fill NaN values in the test feature vectors with the same mean values
fill_nan_values = train_f_vectors.mean()
if not pd.notnull(test_f_vectors).to_numpy().all():
    test_f_vectors.fillna(fill_nan_values, inplace=True)

# Scale the feature vectors (better for some matching methods)
feature_columns = []
for column in train_f_vectors.columns:
    if column not in excl_attributes:
        feature_columns.append(column)

X_train = train_f_vectors[feature_columns]
scaler = StandardScaler().fit(X_train)
X_train_scaled = scaler.transform(X_train)
train_f_vectors[feature_columns] = X_train_scaled

X_test = test_f_vectors[feature_columns]
X_test_scaled = scaler.transform(X_test)
test_f_vectors[feature_columns] = X_test_scaled

# train a matcher
# result = em.select_matcher([dt, svm, rf, lg, ln, nb], table=train_f_vectors, exclude_attrs=excl_attributes, k=5,
#                             target_attr='label', metric_to_select_matcher='f1', random_state=RANDOMSTATE)
# print(result['cv_stats'])


start_time = time.process_time()
matcher.fit(table=train_f_vectors, exclude_attrs=excl_attributes, target_attr='label')
train_time = time.process_time() - start_time

start_time = time.process_time()
if args.method == "SVM":
    prediction = matcher.predict(table=test_f_vectors, exclude_attrs=excl_attributes, append=True, return_probs=False,
                                inplace=False, target_attr='prediction')
    prediction['probability'] = prediction['prediction'].astype(float)
else:
    prediction = matcher.predict(table=test_f_vectors, exclude_attrs=excl_attributes, append=True, return_probs=True,
                                 inplace=False, target_attr='prediction', probs_attr='probability')

eval_time = time.process_time() - start_time
# Step 3. Convert the output into a common format
transform_output(prediction, train_time, eval_time, args.output)
print("Final output: ", os.listdir(args.output))
