import os
import sys

import pandas as pd
import numpy as np
import utils


def transform_input(source_dir, prefixes=['tableA_', 'tableB_'], use_full=True):
    
    tableA_df = pd.read_csv(os.path.join(source_dir, 'tableA.csv'))
    tableB_df = pd.read_csv(os.path.join(source_dir, 'tableB.csv'))
    matches_df = pd.read_csv(os.path.join(source_dir, 'matches.csv'))

    test_df = pd.read_csv(os.path.join(source_dir, 'test.csv'))

    tableA_df.rename(columns=lambda x: x.split('/')[-1], inplace=True)
    tableB_df.rename(columns=lambda x: x.split('/')[-1], inplace=True)
    test_df.rename(columns=lambda x: x.split('/')[-1], inplace=True)

    
    if use_full:
        train_df = pd.read_csv(os.path.join(source_dir, 'train.csv'))
        valid_df = pd.read_csv(os.path.join(source_dir, 'valid.csv'))
        train_df.rename(columns=lambda x: x.split('/')[-1], inplace=True)
        valid_df.rename(columns=lambda x: x.split('/')[-1], inplace=True)

        pair_df = pd.concat([train_df,valid_df, test_df])

        pair_df.rename(lambda x: x.replace(prefixes[0], 'ltable_'), axis='columns', inplace=True)
        pair_df.rename(lambda x: x.replace(prefixes[1], 'rtable_'), axis='columns', inplace=True)
        pair_df['_id'] = np.arange(pair_df.shape[0])

        matches_df.rename(lambda x: x.replace('tableA', 'ltable'), axis='columns', inplace=True)
        matches_df.rename(lambda x: x.replace('tableB', 'rtable'), axis='columns', inplace=True)

        return pair_df, tableA_df, tableB_df, matches_df

    test_df.rename(lambda x: x.replace('tableA', 'ltable'), axis='columns', inplace=True)
    test_df.rename(lambda x: x.replace('tableB', 'rtable'), axis='columns', inplace=True)
    test_df['_id'] = np.arange(test_df.shape[0])

    matches_df.rename(lambda x: x.replace('tableA', 'ltable'), axis='columns', inplace=True)
    matches_df.rename(lambda x: x.replace('tableB', 'rtable'), axis='columns', inplace=True)

    return test_df, tableA_df, tableB_df, matches_df


def transform_output(predictions, results_per_iteration, train_time, eval_time, preprocess_time, dest_dir):
    """
    Transform the output of the method into two common format files, which are stored in the destination directory.
    metrics.csv: f1, precision, recall, train_time, eval_time (1 row, 5 columns, with header)
    predictions.csv: tableA_id, tableB_id, etc. (should have at least 2 columns and a header row)
    """

    predictions['prob_class1'] = np.clip(predictions['pred']+utils.DEL, 0., 1.)
    predictions['prediction'] = np.round(np.clip(predictions['pred'] + utils.DEL, 0., 1.)).astype(int)
    p_table = predictions[['ltable_id', 'rtable_id', 'gold', 'prob_class1']]
    p_table.columns = p_table.columns = ['tableA_id', 'tableB_id', 'label', 'prob_class1']
    candidate_table = predictions[predictions['prediction'] == 1]
    # save candidate pair IDs to predictions.csv
    p_table.to_csv(os.path.join(dest_dir, 'predictions.csv'), index=False)

    # calculate evaluation metrics
    num_candidates = candidate_table.shape[0]
    true_positives = candidate_table['gold'].sum()
    ground_truth = predictions['gold'].sum()

    recall = true_positives / ground_truth
    precision = true_positives / num_candidates
    f1 = 2 * precision * recall / (precision + recall)

    pd.DataFrame({
        'f1': [f1],
        'precision': [true_positives / num_candidates],
        'recall': [true_positives / ground_truth],
        'preprocess_time': [preprocess_time],
        'train_time': [train_time],
        'eval_time': [eval_time],
    }).to_csv(os.path.join(dest_dir, 'metrics.csv'), index=False)

    pd.DataFrame(results_per_iteration,
                 columns=['iteration', 'f1', 'precision', 'recall', 'iteration_time', 'eval_time']
                 ).to_csv(os.path.join(dest_dir, 'metrics_per_iteration.csv'), index=False)

    return None


if __name__ == "__main__":
    in_path = sys.argv[1]
    out_path = sys.argv[2]

    if not os.path.isdir(out_path):
        os.mkdir(out_path)

    transform_input(in_path)
