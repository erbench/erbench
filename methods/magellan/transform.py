import os
import pandas as pd


def transform_output(predictions_df, train_time, eval_time, dest_dir):
    """
    Transform the output of the method into two common format files, which are stored in the destination directory.
    metrics.csv: f1, precision, recall, train_time, eval_time (1 row, 5 columns, with header)
    predictions.csv: tableA_id, tableB_id, etc. (should have at least 2 columns and a header row)
    """

    # get the actual candidates (entity pairs with prediction 1)
    candidate_table = predictions_df[predictions_df['prediction'] == 1]
    # save candidate pair IDs to predictions.csv
    name_cols = list(sorted([col for col in predictions_df.columns if col.endswith('_name') or col.endswith('_title')]))
    predictions_df = predictions_df[['tableA_id', 'tableB_id']+name_cols+['label', 'probability']]
    predictions_df.columns = ['tableA_id', 'tableB_id', 'tableA_name', 'tableB_name', 'label', 'prob_class1']
    predictions_df.to_csv(os.path.join(dest_dir, 'predictions.csv'), index=False)
    #candidate_table[['tableA_id', 'tableB_id']].to_csv(os.path.join(dest_dir, 'predictions.csv'), index=False)

    # calculate evaluation metrics
    num_candidates = candidate_table.shape[0]
    true_positives = candidate_table['label'].sum()
    ground_truth = predictions_df['label'].sum()

    recall = true_positives / ground_truth
    precision = true_positives / num_candidates
    f1 = 2 * precision * recall / (precision + recall)

    pd.DataFrame({
        'f1': [f1],
        'precision': [true_positives / num_candidates],
        'recall': [true_positives / ground_truth],
        'train_time': [train_time],
        'eval_time': [eval_time],
    }).to_csv(os.path.join(dest_dir, 'metrics.csv'), index=False)

    return None
