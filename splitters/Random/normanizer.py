import os
import argparse
import pathtype
import pandas as pd
from detect_delimiter import detect

d_info = {
    'D1': ['rest1', 'rest2', '|'],
    'D2': ['abt', 'buy', '|'],
    'D3': ['amazon', 'gp', '#'],
    'D4': ['dblp', 'acm', '%'],
    'D5': ['imdb', 'tmdb', '|'],
    'D6': ['imdb', 'tvdb', '|'],
    'D7': ['tmdb', 'tvdb', '|'],
    'D8': ['walmart', 'amazon', '|'],
    'D9': ['dblp', 'scholar', '>'],
    'D10': ['imdb', 'dbpedia', '|']
}


def get_delimiter(file_path):
    data = open(file_path, "r", encoding="utf8").readline()
    return detect(data, default=',', whitelist=[',', ';', '|', '%', '>', '#'])


def rename_file(file_name, dataset_name=""):
    if file_name.endswith("clean.csv"):
        file_name = file_name.replace("clean.csv", ".csv")

    if file_name == "gt.csv":
        return "matches.csv"

    for key in d_info.keys():
        if key.lower() in dataset_name:
            if d_info[key][0] in file_name:
                return "tableA.csv"
            if d_info[key][1] in file_name:
                return "tableB.csv"

    return file_name


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Merges the test and train datasets to create matches pairs')
    parser.add_argument('input', type=pathtype.Path(readable=True), nargs='?', default='/data',
                        help='Input directory containing the dataset')
    parser.add_argument('output', type=str, nargs='?',
                        help='Output directory to store the output. If not provided, input directory will be used')
    args = parser.parse_args()

    if args.output is None:
        args.output = args.input

    if '/' not in args.output:
        args.output = os.path.join(args.input, args.output)

    os.makedirs(args.output, exist_ok=True)
    if not os.path.isdir(args.output) or not os.access(args.output, os.W_OK):
        print("output folder does not exits or is not writable")
        exit(1)

    print("Hi, I'm normalizer, I'm checking if csv separator is consistent.")

    files = [f for f in os.listdir(args.input) if f.endswith('.csv')]

    for file in files:
        print("Reading", file)
        save_file_name = rename_file(file, os.path.basename(args.input))

        sep = get_delimiter(os.path.join(args.input, file))
        df = pd.read_csv(os.path.join(args.input, file), encoding_errors='replace', sep=sep)

        if sep != ',':
            df = pd.read_csv(os.path.join(args.input, file), encoding_errors='replace', sep=sep)
            print("Found non-standard separator {}".format(sep))

        if save_file_name == 'matches.csv' and 'D1' in df.columns:
            df = df.rename(columns={'D1': 'tableA_id', 'D2': 'tableB_id'})
            print("Renamed columns D1 and D2 to tableA_id and tableB_id")

        if save_file_name == 'tableA.csv' or save_file_name == 'tableB.csv':
            if 'id' not in df.columns:
                raise ValueError("No id column found in the dataset")

        if file != save_file_name:
            os.unlink(os.path.join(args.input, file))
            print("Deleted source file", file)

        df.to_csv(os.path.join(args.output, save_file_name), index=False)
