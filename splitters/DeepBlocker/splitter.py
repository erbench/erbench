import sys
sys.path.append('fork-deepblocker')

import argparse
import os
import random
import pathtype
import pandas as pd
from deep_blocker import DeepBlocker
from tuple_embedding_models import AutoEncoderTupleEmbedding
from vector_pairing_models import ExactTopKVectorPairing
from sklearn.model_selection import train_test_split
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
from settings import dataset_settings

def clean_entry(entry, stemmer, stop_words):
    try:
        list_entries = word_tokenize(entry)
    except LookupError:
        nltk.download('punkt_tab')
        list_entries = word_tokenize(entry)
    clean_entries = [stemmer.stem(e) for e in list_entries if e not in stop_words]
    return ' '.join(clean_entries)

def generate_candidates(embedding_path, tableA_df, tableB_df, matches_df, settings):
    for col in tableA_df.columns:
        if col == 'id':
            continue
        tableA_df[col] = tableA_df[col].astype(str)
        tableA_df[col] = tableA_df[col].str.replace('\t', ' ')
    for col in tableB_df.columns:
        if col == 'id':
            continue
        tableB_df[col] = tableB_df[col].astype(str)
        tableB_df[col] = tableB_df[col].str.replace('\t', ' ')
    cols_to_block = list(set(tableA_df.columns.tolist()) & set(tableB_df.columns.tolist()))
    cols_to_block.remove('id')
    print("Blocking columns: ", cols_to_block)
    # tableA_df[cols_to_block] = tableA_df[cols_to_block].astype(str)
    # tableB_df[cols_to_block] = tableB_df[cols_to_block].astype(str)
    # for col in cols_to_block:
    #     tableA_df[col] = tableA_df[col].str.replace('\t', ' ')
    #     tableB_df[col] = tableB_df[col].str.replace('\t', ' ')
    block_A = tableA_df.copy()
    block_B = tableB_df.copy()

    if settings['clean']:
        try:
            stop_words = set(stopwords.words('english'))
        except LookupError:
            nltk.download('stopwords')
            stop_words = set(stopwords.words('english'))
        snowball_stemmer = SnowballStemmer('english')
        block_A[cols_to_block] = block_A[cols_to_block].map(lambda x: clean_entry(x, snowball_stemmer, stop_words))
        block_B[cols_to_block] = block_B[cols_to_block].map(lambda x: clean_entry(x, snowball_stemmer, stop_words))

    #golden_df = matches_df.rename(columns={'tableA_id': 'ltable_id', 'tableB_id': 'rtable_id'})

    tuple_embedding_model = AutoEncoderTupleEmbedding(embedding_path=embedding_path)
    topK_vector_pairing_model = ExactTopKVectorPairing(K=settings['K'])
    db = DeepBlocker(tuple_embedding_model, topK_vector_pairing_model)

    if settings['reverse']:
        candidate_set_df = db.block_datasets(block_B, block_A, cols_to_block)
        candidate_set_df['tableA_id'] = block_A['id'].to_numpy()[candidate_set_df['rtable_id'].to_numpy()]
        candidate_set_df['tableB_id'] = block_B['id'].to_numpy()[candidate_set_df['ltable_id'].to_numpy()]
    else:
        candidate_set_df = db.block_datasets(block_A, block_B, cols_to_block)
        candidate_set_df['tableA_id'] = block_A['id'].to_numpy()[candidate_set_df['ltable_id'].to_numpy()]
        candidate_set_df['tableB_id'] = block_B['id'].to_numpy()[candidate_set_df['rtable_id'].to_numpy()]

    #golden_df['label'] = 1
    #candidate_set_df['label'] = 0
    #pairs_df = pd.concat([golden_df, candidate_set_df]).drop_duplicates(subset=['ltable_id', 'rtable_id'], keep='first')

    #Alternative Way for pairs_df (only keeps those true pairs, which were found in blocking)
    golden_set = set(matches_df.itertuples(index=False, name=None))
    pairs_df = candidate_set_df[['tableA_id', 'tableB_id']]
    pairs_df['label'] = pairs_df.apply(lambda x: (x['tableA_id'], x['tableB_id']) in golden_set, axis=1).astype(int)

    ## Sanity Check:
    print(pairs_df['label'].sum()/pairs_df.shape[0], pairs_df['label'].sum()/matches_df.shape[0])

    cand_tableA = tableA_df.add_prefix('tableA_')
    cand_tableB = tableB_df.add_prefix('tableB_')

    return pd.concat([
        (cand_tableA.loc[pairs_df['tableA_id']]).reset_index(drop=True),
        (cand_tableB.loc[pairs_df['tableB_id']]).reset_index(drop=True),
        pairs_df['label'].reset_index(drop=True)
    ], axis=1)


def split_input(embedding_path, tableA_df, tableB_df, matches_df, settings, seed=1, valid=True):
    candidates = generate_candidates(embedding_path, tableA_df, tableB_df, matches_df, settings)
    print("Candidates generated: ", candidates.shape[0])
    if valid:
        train, test_valid = train_test_split(candidates, train_size=0.6, random_state = seed, shuffle = True, stratify = candidates['label'])
        valid, test = train_test_split(test_valid, train_size=0.5, random_state = seed, shuffle = True, stratify = test_valid['label'])
        return (train, valid, test)

    return train_test_split(candidates, train_size=0.75, random_state=seed, shuffle=True, stratify=candidates['label'])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Splits the dataset using DeepBlocker method')
    parser.add_argument('input', type=pathtype.Path(readable=True), nargs='?', default='/data',
                        help='Input directory containing the dataset')
    parser.add_argument('output', type=str, nargs='?',
                        help='Output directory to store the output. If not provided, the input directory will be used')
    parser.add_argument('--embeddings', type=pathtype.Path(readable=True), nargs='?', default='/workspace/embeddings',
                    help='The directory where embeddings are stored')
    parser.add_argument('-r', '--recall', type=float, nargs='?', default=0.9,
                        help='The recall value for the train set')
    args = parser.parse_args()

    if args.output is None:
        args.output = args.input

    os.makedirs(args.output, exist_ok=True)
    if not os.path.isdir(args.output) or not os.access(args.output, os.W_OK):
        print("output folder does not exits or is not writable")
        exit(1)

    print("Hi, I'm DeepBlocker splitter, I'm doing random split of the input datasets into train and test sets.")
    tableA_df = pd.read_csv(os.path.join(args.input, 'tableA.csv'), encoding_errors='replace')
    tableB_df = pd.read_csv(os.path.join(args.input, 'tableB.csv'), encoding_errors='replace')
    matches_df = pd.read_csv(os.path.join(args.input, 'matches.csv'), encoding_errors='replace')

    tableA_df = tableA_df.set_index('id', drop=False)
    tableB_df = tableB_df.set_index('id', drop=False)

    #Remove those pairs from matches, which entries no longer appear in tableA or tableB:
    A_match_exists = matches_df['tableA_id'].map(lambda x: x in tableA_df.index).astype(bool)
    B_match_exists = matches_df['tableB_id'].map(lambda x: x in tableB_df.index).astype(bool)
    matches_df = matches_df[A_match_exists & B_match_exists]

    print("Input tables are:", "A", tableA_df.shape, "B", tableB_df.shape, "Matches", matches_df.shape)

    # get right settings:
    folders = [entry for entry in str(args.input).split('/') if entry != '']
    dataset_folder = folders[-1]
    dataset = dataset_folder.split('_')[0]
    settings = dataset_settings[args.recall][dataset]

    train, valid, test = split_input(str(args.embeddings), tableA_df, tableB_df, matches_df, seed=random.randint(0, 4294967295), settings=settings, valid=True)
    print("Done! Train size: {}, test size: {}.".format(train.shape[0], test.shape[0]))



    train.to_csv(os.path.join(output_folder, "train.csv"), index=False)
    valid.to_csv(os.path.join(output_folder, "valid.csv"), index=False)
    test.to_csv(os.path.join(output_folder, "test.csv"), index=False)

    tableA_df.to_csv(os.path.join(output_folder, "tableA.csv"), index=False)
    tableB_df.to_csv(os.path.join(output_folder, "tableB.csv"), index=False)
    matches_df.to_csv(os.path.join(output_folder, "matches.csv"), index=False)
