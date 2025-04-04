import argparse
from os import path
import pathtype
import pandas as pd


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Merges the test and train datasets to create matches pairs')
    parser.add_argument('input', type=pathtype.Path(readable=True), nargs='?', default='/data',
                        help='Input directory containing the dataset')
    parser.add_argument('output', type=pathtype.Path(writable=True), nargs='?',
                        help='Output directory to store the output. If not provided, input directory will be used')
    args = parser.parse_args()

    if args.output is None:
        args.output = args.input

    print("Hi, I'm merger, I'm creating matches file based on split datasets.")
    test_df = pd.read_csv(path.join(args.input, 'test.csv'), encoding_errors='replace')
    train_df = pd.read_csv(path.join(args.input, 'train.csv'), encoding_errors='replace')
    try:
        valid_df = pd.read_csv(path.join(args.input, 'valid.csv'), encoding_errors='replace')
    except FileNotFoundError:
        valid_df = pd.DataFrame() # empty df
    print("Input tables are:", "test", test_df.shape, "train", train_df.shape, "valid", valid_df.shape)

    matches_df = pd.concat([test_df, train_df, valid_df]) # merge all dfs
    matches_df = matches_df[matches_df['label'] == 1] # keep only matches

    if 'table1.id' in matches_df.columns:
        matches_df = matches_df.rename(columns={'table1.id': 'tableA_id', 'table2.id': 'tableB_id'})

    matches_df = matches_df[['tableA_id', 'tableB_id']] # keep only relevant columns
    matches_df = matches_df.drop_duplicates().sort_values(by='tableA_id')

    print("Done! Found {} matches.".format(matches_df.shape[0]))

    matches_df.to_csv(path.join(args.output, "matches.csv"), index=False)
