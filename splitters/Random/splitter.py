import sys
import argparse
from os import path
import os
import random
import pathtype
import pandas as pd
import numpy as np
from itertools import product
from sklearn.model_selection import train_test_split
import time


def generate_candidates(tableA_df, tableB_df, matches_df, recall=0.7, neg_pairs_ratio=10, seed=1):

    ac_tableA = list(tableA_df.columns)
    ac_tableA.remove('id')
    ac_tableB = list(tableB_df.columns)
    ac_tableB.remove('id')

    tableA_df[ac_tableA] = tableA_df[ac_tableA].astype(str)
    for col in ac_tableA:
        tableA_df[col] = tableA_df[col].str.replace('\t', ' ')
    tableB_df[ac_tableB] = tableB_df[ac_tableB].astype(str)
    for col in ac_tableB:
        tableB_df[col] = tableB_df[col].str.replace('\t', ' ')

    # rename columns of tableA and tableB for an easier joining of DataFrames
    cand_tableA = tableA_df.add_prefix('tableA_')
    cand_tableB = tableB_df.add_prefix('tableB_')

    # create table of matching pairs, which contains all attributes
    red_matches = matches_df.sample(frac=recall, random_state=seed, axis=0, replace=False)
    pos_pairs = pd.concat([
        (cand_tableA.loc[red_matches['tableA_id']]).reset_index(drop=True),
        (cand_tableB.loc[red_matches['tableB_id']]).reset_index(drop=True)
    ], axis=1)

    assert np.array_equal(matches_df.loc[red_matches.index,:].to_numpy(), pos_pairs.loc[:, ['tableA_id', 'tableB_id']].to_numpy()), \
        "Positive pair creation failed, pairs not identical with matches.csv"

    # create table of (randomly sampled) non-matching pairs, again containing all necessary attributes
    golden_set = set(matches_df.itertuples(index=False, name=None))

    if neg_pairs_ratio == -1:
        full_pairs = set(tuple(pair for pair in product(tableA_df['id'], tableB_df['id'])))
        neg_tuples = full_pairs - golden_set
        neg_ids = np.array(list(neg_tuples))
    else:
        neg_pairs_limit = int(neg_pairs_ratio * len(golden_set) * recall)
        rng = np.random.default_rng(seed)
        skip_counter = 0
        a_id = rng.choice(tableA_df['id'].to_numpy(), size=(neg_pairs_limit))
        b_id = rng.choice(tableB_df['id'].to_numpy(), size=(neg_pairs_limit))
        neg_ids = set(zip(a_id, b_id))
        neg_ids = neg_ids - golden_set
        num_neg_pairs = len(neg_ids)

        while num_neg_pairs < neg_pairs_limit:
            assert skip_counter < neg_pairs_limit * 1.5, "Too many pairs skipped, please check the number of negatives requested"
            a_id = rng.choice(tableA_df['id'].to_numpy())
            b_id = rng.choice(tableB_df['id'].to_numpy())

            if (a_id, b_id) in golden_set or (a_id, b_id) in neg_ids:
                skip_counter += 1
                continue
            neg_ids.add((a_id, b_id))
            num_neg_pairs += 1
        neg_ids = np.array(list(neg_ids))

    neg_pairs = pd.concat([
        (cand_tableA.loc[neg_ids[:, 0]]).reset_index(drop=True),
        (cand_tableB.loc[neg_ids[:, 1]]).reset_index(drop=True)
    ], axis=1)

    pos_pairs['label'] = 1
    neg_pairs['label'] = 0

    # join the matching and non-matching pairs to a large table
    pairs = pd.concat([pos_pairs, neg_pairs]).reset_index(drop=True)
    return pairs

def split_input(tableA_df, tableB_df, matches_df, recall=0.9, neg_pairs_ratio=10, seed=1, valid=True):
    candidates = generate_candidates(tableA_df, tableB_df, matches_df, recall=recall,
                                     neg_pairs_ratio=neg_pairs_ratio, seed=seed)

    # get statistics:
    num_matches = matches_df.shape[0]
    num_candidates = candidates.shape[0]
    tp = candidates['label'].sum()
    p = tp / num_candidates
    r = tp / num_matches
    f1 = 2 * p * r / (p + r)
    stats = [f1, p, r, num_candidates]

    print("Candidates generated: ", candidates.shape[0])
    if valid:
        train, test_valid = train_test_split(candidates, train_size=0.6, random_state=seed, shuffle=True,
                                             stratify=candidates['label'])
        valid, test = train_test_split(test_valid, train_size=0.5, random_state=seed, shuffle=True,
                                       stratify=test_valid['label'])

        return train, valid, test, stats
    train, test = train_test_split(candidates, train_size=0.75,
                                   random_state=seed, shuffle=True, stratify=candidates['label'])
    return train, test, stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Splits the dataset using random method')
    parser.add_argument('input', type=pathtype.Path(readable=True), nargs='?', default='/data',
                        help='Input directory containing the dataset')
    parser.add_argument('output', type=str, nargs='?',
                        help='Output directory to store the output. If not provided, the input directory will be used')
    parser.add_argument('-r', '--recall', type=float, nargs='?', default=0.9,
                        help='The recall value for the train set')
    parser.add_argument('-np', '--neg_pairs_ratio', type=float, nargs='?', default=10,
                        help='The ratio of negative pairs to be generated relative to the number of positive pairs')
    parser.add_argument('-s', '--seed', type=int, nargs='?', default=random.randint(0, 4294967295),
                        help='The random state used to initialize the algorithms and split dataset')
    args = parser.parse_args()

    if args.output is None:
        args.output = args.input

    os.makedirs(args.output, exist_ok=True)
    if not os.path.isdir(args.output) or not os.access(args.output, os.W_OK):
        print("output folder does not exits or is not writable")
        exit(1)

    print("Hi, I'm simple splitter, I'm doing random split of the input datasets into train and test sets.")
    tableA_df = pd.read_csv(path.join(args.input, 'tableA.csv'), encoding_errors='replace')
    tableB_df = pd.read_csv(path.join(args.input, 'tableB.csv'), encoding_errors='replace')
    matches_df = pd.read_csv(path.join(args.input, 'matches.csv'), encoding_errors='replace')

    tableA_df.set_index('id', inplace=True, drop=False)
    tableB_df.set_index('id', inplace=True, drop=False)

    # Remove those pairs from matches, which entries no longer appear in tableA or tableB:
    A_match_exists = matches_df['tableA_id'].map(lambda x: x in tableA_df['id']).astype(bool)
    B_match_exists = matches_df['tableB_id'].map(lambda x: x in tableB_df['id']).astype(bool)
    matches_df = matches_df[A_match_exists & B_match_exists]
    print("Input tables are:", "A", tableA_df.shape, "B", tableB_df.shape, "Matches", matches_df.shape)

    # split the input datasets
    start_time = time.process_time()
    train, valid, test, stats = split_input(tableA_df, tableB_df, matches_df, recall=args.recall,
                                     neg_pairs_ratio=args.neg_pairs_ratio, seed=args.seed)
    stop_time = time.process_time()
    print("Done! Train size: {}, test size: {}.".format(train.shape[0], test.shape[0]))

    train.to_csv(path.join(args.output, "train.csv"), index=False)
    valid.to_csv(path.join(args.output, "valid.csv"), index=False)
    test.to_csv(path.join(args.output, "test.csv"), index=False)

    tableA_df.to_csv(os.path.join(args.output, 'tableA.csv'), index=False)
    tableB_df.to_csv(os.path.join(args.output, 'tableB.csv'), index=False)
    matches_df.to_csv(os.path.join(args.output, 'matches.csv'), index=False)

    metrics_file = open(os.path.join(args.output, "filtering_metrics.txt"), 'w')
    cols = ['f1', 'precision', 'recall', 'filtering_time', 'num_candidates', 'entries_tableA', 'entries_tableB',
            'entries_matches']
    stats = stats[:3] + [stop_time - start_time] + [stats[3]] + [tableA_df.shape[0], tableB_df.shape[0],
                                                                 matches_df.shape[0]]
    print(*cols, file=metrics_file, sep=',')
    print(*stats, file=metrics_file, sep=',')
    metrics_file.close()

