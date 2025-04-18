import sys
sys.path.append('fork-deepblocker')

import argparse
import os
import time
import random
import pathtype

import pandas as pd
from pyjedai.joins import TopKJoin
from pyjedai.datamodel import Data
from settings import dataset_settings
from sklearn.model_selection import train_test_split
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer


def clean_entry(entry, stemmer, stop_words):
    list_entries = word_tokenize(entry)
    clean_entries = [stemmer.stem(e) for e in list_entries if e not in stop_words]
    return ' '.join(clean_entries)

def generate_candidates(tableA_df, tableB_df, matches_df, settings):

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

    block_A = tableA_df.copy()
    block_B = tableB_df.copy()
    print(block_A['id'], block_B['id'])

    if settings['clean']:
        stop_words = set(stopwords.words('english'))
        snowball_stemmer = SnowballStemmer('english')
        block_A[ac_tableA] = block_A[ac_tableA].map(lambda x: clean_entry(x, snowball_stemmer, stop_words))
        block_B[ac_tableB] = block_B[ac_tableB].map(lambda x: clean_entry(x, snowball_stemmer, stop_words))

    if settings['reverse']:
        data = Data(
            dataset_1=block_B,
            dataset_2=block_A,
            id_column_name_1 = 'id',
            id_column_name_2 = 'id',
            attributes_1 = ac_tableB,
            attributes_2 = ac_tableA,
        )
    else:
        data = Data(
            dataset_1=block_A,
            dataset_2=block_B,
            id_column_name_1='id',
            id_column_name_2='id',
            attributes_1=ac_tableA,
            attributes_2=ac_tableB,
        )
    if settings['QGram'] == 0:
        tokenization = 'standard'
    else:
        tokenization = 'qgrams'
    if settings['multiset']:
        tokenization += '_multiset'
    join = TopKJoin(K = settings['K'], metric = settings['similarity'], tokenization = tokenization, qgrams = settings['QGram'])

    candidates = join.fit(data)
    candidates_df = join.export_to_df(candidates)
    candidates_df = candidates_df.astype(int)
    if settings['reverse']:
        candidates_df.columns = ['tableB_id', 'tableA_id']
    else:
        candidates_df.columns = ['tableA_id', 'tableB_id']

    #only keeps those true pairs, which were found in blocking
    golden_set = set(matches_df.itertuples(index=False, name=None))
    pairs_df = candidates_df
    pairs_df['label'] = pairs_df.apply(lambda x: (x['tableA_id'], x['tableB_id']) in golden_set, axis=1).astype(int)

    ## Sanity Check:
    print(pairs_df['label'].sum() / pairs_df.shape[0], pairs_df['label'].sum() / matches_df.shape[0])

    cand_tableA = tableA_df.add_prefix('tableA_')
    cand_tableB = tableB_df.add_prefix('tableB_')

    return pd.concat([
        (cand_tableA.loc[pairs_df['tableA_id']]).reset_index(drop=True),
        (cand_tableB.loc[pairs_df['tableB_id']]).reset_index(drop=True),
        pairs_df['label'].reset_index(drop=True)
    ], axis=1)


def split_input(tableA_df, tableB_df, matches_df, settings, seed = 1, valid=True):
    candidates = generate_candidates(tableA_df, tableB_df, matches_df, settings)

    #get statistics:
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

    return train_test_split(candidates, train_size=0.75, random_state=seed, shuffle=True, stratify=candidates['label']), stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Splits the dataset using KNN-Join method')
    parser.add_argument('input', type=pathtype.Path(readable=True), nargs='?', default='/data',
                        help='Input directory containing the dataset')
    parser.add_argument('output', type=str, nargs='?',
                        help='Output directory to store the output. If not provided, the input directory will be used')
    parser.add_argument('-r', '--recall', type=float, nargs='?', default=0.9,
                        help='The recall value for the train set')
    parser.add_argument('-s', '--seed', type=int, nargs='?', default=random.randint(0, 4294967295),
                        help='The random state used to initialize the algorithms and split dataset')
    parser.add_argument('-d', '--default', action='store_true', default=False,
                        help='use the default configuration for kNN-Join')
    args = parser.parse_args()

    if args.output is None:
        args.output = args.input

    os.makedirs(args.output, exist_ok=True)
    if not os.path.isdir(args.output) or not os.access(args.output, os.W_OK):
        print("output folder does not exits or is not writable")
        exit(1)

    print("Hi, I'm KNN-Join splitter, I'm splitting the candidates of KNN-Join into train and test sets.")
    tableA_df = pd.read_csv(os.path.join(args.input, 'tableA.csv'), encoding_errors='replace')
    tableB_df = pd.read_csv(os.path.join(args.input, 'tableB.csv'), encoding_errors='replace')
    matches_df = pd.read_csv(os.path.join(args.input, 'matches.csv'), encoding_errors='replace')

    tableA_df = tableA_df.set_index('id', drop=False)
    tableB_df = tableB_df.set_index('id', drop=False)

    #Remove those pairs from matches, which entries no longer appear in tableA or tableB:
    A_match_exists = matches_df['tableA_id'].map(lambda x: x in tableA_df['id']).astype(bool)
    B_match_exists = matches_df['tableB_id'].map(lambda x: x in tableB_df['id']).astype(bool)
    matches_df = matches_df[A_match_exists & B_match_exists]

    print("Input tables are:", "A", tableA_df.shape, "B", tableB_df.shape, "Matches", matches_df.shape)

    #get right settings:
    folders =[entry for entry in str(args.input).split('/') if entry != '']
    dataset_folder = folders[-1]
    dataset = dataset_folder.split('_')[0]

    if args.default:
        settings = {'clean':True, 'reverse':False, 'QGram': 5, 'multiset': True, 'similarity':'cosine', 'K':5}
        if tableA_df.shape[0]<tableB_df.shape[0]:
            settings['reverse'] = True
    else:
        settings = dataset_settings[args.recall][dataset]


    start_time = time.process_time()
    train, valid, test, stats = split_input(tableA_df, tableB_df, matches_df,
                                     seed=args.seed, settings=settings, valid=True)
    stop_time = time.process_time()
    print("Done! Train size: {}, test size: {}.".format(train.shape[0], test.shape[0]))

    train.to_csv(os.path.join(args.output, "train.csv"), index=False)
    valid.to_csv(os.path.join(args.output, "valid.csv"), index=False)
    test.to_csv(os.path.join(args.output, "test.csv"), index=False)

    tableA_df.to_csv(os.path.join(args.output, "tableA.csv"), index=False)
    tableB_df.to_csv(os.path.join(args.output, "tableB.csv"), index=False)
    matches_df.to_csv(os.path.join(args.output, "matches.csv"), index=False)

    pd.DataFrame({
        'f1': [stats[0]],
        'precision': [stats[1]],
        'recall': [stats[2]],
        'filtering_time': [stop_time - start_time],
        'num_candidates': [stats[3]],
        'entries_tableA': [tableA_df.shape[0]],
        'entries_tableB': [tableB_df.shape[0]],
        'entries_matches': [matches_df.shape[0]],
    }).to_csv(os.path.join(args.output, 'filtering_metrics.csv'), index=False)
