import os
import sys

import pandas as pd
import torch


def join_columns(table, columns_to_join=None, separator=' ', prefixes=['tableA_', 'tableB_']):
    agg_table = pd.DataFrame()
    for prefix in prefixes:
        if columns_to_join == None:
            columns = [column for column in table.columns if (column != prefix + 'id' and prefix in column)]
        else:
            columns = [prefix + column for column in columns_to_join]

        red_table = table.loc[:, columns]
        red_table = red_table.fillna('')
        red_table = red_table.astype(str)

        part_table = red_table.aggregate(separator.join, axis=1)
        # part_table = part_table.map(lambda x: x.replace('nan', ''))
        part_table.rename(prefix + 'AgValue', inplace=True)

        agg_table = pd.concat([agg_table, table[prefix + 'id'], part_table], axis=1)

    return pd.concat([agg_table, table['label']], axis=1)


def transform_input(source_dir, columns_to_join=None, separator=' ', prefixes=['tableA_', 'tableB_']):
    train_df = pd.read_csv(os.path.join(source_dir, 'train.csv'), encoding_errors='replace')
    valid_df = pd.read_csv(os.path.join(source_dir, 'valid.csv'), encoding_errors='replace')
    test_df = pd.read_csv(os.path.join(source_dir, 'test.csv'), encoding_errors='replace')

    train = join_columns(train_df, columns_to_join, separator, prefixes)
    valid = join_columns(valid_df, columns_to_join, separator, prefixes)
    test = join_columns(test_df, columns_to_join, separator, prefixes)

    return train, valid, test


def transform_output(predictions_df, logits, test_table, results_per_epoch, train_time, eval_time, dest_dir):
    """
    Transform the output of the method into two common format files, which are stored in the destination directory.
    metrics.csv: f1, precision, recall, train_time, eval_time (1 row, 5 columns, with header)
    predictions.csv: tableA_id, tableB_id, etc. (should have at least 2 columns and a header row)
    """
    sm = torch.nn.Softmax(dim=1)
    probs = sm(torch.Tensor(logits))
    predictions_df.rename(columns={'labels': 'label'}, inplace=True)
    predictions_df['prob_class1'] = probs[:, 1].tolist()
    predictions_df['tableA_id'] = test_table.loc[predictions_df.index, 'tableA_id']
    predictions_df['tableB_id'] = test_table.loc[predictions_df.index, 'tableB_id']
    predictions_df[['tableA_id', 'tableB_id', 'label', 'prob_class1']].to_csv(os.path.join(dest_dir, 'predictions.csv'), index=False)
    # get the actual candidates (entity pairs with prediction 1)
    #candidate_ids = predictions_df[predictions_df['predictions'] == 1]
    #candidate_table = test_table.iloc[candidate_ids.index]
    # save candidate pair IDs to predictions.csv
    #candidate_table[['tableA_id', 'tableB_id']].to_csv(os.path.join(dest_dir, 'predictions.csv'), index=False)
    
    if predictions_df['predictions'].sum() > 0:
        # calculate evaluation metrics
        num_candidates = predictions_df['predictions'].sum()
        true_positives = predictions_df.loc[predictions_df['predictions'] == 1, 'label'].sum()
        ground_truth = predictions_df['label'].sum()
        recall = true_positives / ground_truth
        precision = true_positives / num_candidates
        f1 = 2 * precision * recall / (precision + recall)
    else:
        f1 = 0
        precision = 0
        recall = 0

    pd.DataFrame({
        'f1': [f1],
        'precision': [precision],
        'recall': [recall],
        'train_time': [train_time],
        'eval_time': [eval_time],
    }).to_csv(os.path.join(dest_dir, 'metrics.csv'), index=False)

    pd.DataFrame(results_per_epoch,
                 columns=['epoch', 'f1', 'precision', 'recall', 'train_time', 'valid_time', 'test_time']
                 ).to_csv(os.path.join(dest_dir, 'metrics_per_epoch.csv'), index=False)

    return None


if __name__ == "__main__":
    in_path = sys.argv[1]
    out_path = sys.argv[2]

    if not os.path.isdir(out_path):
        os.mkdir(out_path)

    transform_input(in_path)
