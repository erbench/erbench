import os
import pandas as pd
import torch

def transform_input(source_dir, output_dir, prefixes=['tableA_', 'tableB_']):
    train_data = pd.read_csv(os.path.join(source_dir, 'train.csv'), encoding_errors='replace')
    test_data = pd.read_csv(os.path.join(source_dir, 'test.csv'), encoding_errors='replace')
    valid_data = pd.read_csv(os.path.join(source_dir, 'valid.csv'), encoding_errors='replace')
    train_data.drop(columns = ['tableA_id', 'tableB_id'], inplace=True)
    test_data.drop(columns = ['tableA_id', 'tableB_id'], inplace=True)
    valid_data.drop(columns = ['tableA_id', 'tableB_id'], inplace=True)

    A_columns = [col[len(prefixes[0]):] for col in train_data.columns
                 if col.startswith(prefixes[0])]
    B_columns = [col[len(prefixes[1]):] for col in train_data.columns
                 if col.startswith(prefixes[1])]

    if len(A_columns) != len(B_columns):
        cc = set(A_columns) & set(B_columns)
        print('Original number of columns table A: ', len(A_columns))
        print('Original number of columns table B: ', len(B_columns))
        print('Reduced number of columns: ', len(cc))
        final_columns = [col for col in train_data.columns
                         if (col[len(prefixes[0]):] in cc
                             or col[len(prefixes[1]):] in cc
                             or not col.startswith(tuple(prefixes)))]
        print(final_columns)
        train_data = train_data[final_columns]
        valid_data = valid_data[final_columns]
        test_data = test_data[final_columns]

    train_data.to_csv(os.path.join(output_dir, 'train_dm.csv'), index_label='id')
    test_data.to_csv(os.path.join(output_dir, 'test_dm.csv'), index_label='id')
    valid_data.to_csv(os.path.join(output_dir, 'valid_dm.csv'), index_label='id')
    return None

def transform_output(predictions, data, stats, results_per_epoch, train_time, eval_time, dest_dir):
    """
    Transform the output of the method into two common format files, which are stored in the destination directory.
    metrics.csv: f1, precision, recall, train_time, eval_time (1 row, 5 columns, with header)
    predictions.csv: match_score, tableA_id, tableB_id, etc.
    """
    sm = torch.nn.Softmax(dim=1)
    predictions = pd.DataFrame(predictions, columns=['id', 'score1', 'score2'])
    predictions['id'] = predictions['id'].astype(int)
    probs = torch.Tensor(predictions[['score1', 'score2']].to_numpy())
    probs = sm(probs)
    predictions['prob_class1'] = probs[:, 1].tolist()
    #print(predictions)

    #predictions = predictions[predictions['score2']>predictions['score1']]
    predictions['tableA_id'] = data.loc[predictions['id'], 'tableA_id']
    predictions['tableB_id'] = data.loc[predictions['id'], 'tableB_id']
    predictions['label'] = data.loc[predictions['id'], 'label']

    predictions.loc[:,['tableA_id', 'tableB_id', 'label', 'prob_class1']].to_csv(os.path.join(dest_dir, 'predictions.csv'), index=False)

    pd.DataFrame({
        'f1': [stats.f1().item()],
        'precision': [stats.precision().item()],
        'recall': [stats.recall().item()],
        'train_time': [train_time],
        'eval_time': [eval_time],
    }).to_csv(os.path.join(dest_dir, 'metrics.csv'), index=False)

    pd.DataFrame(results_per_epoch,
                 columns=['epoch', 'f1', 'precision', 'recall', 'train_time', 'valid_time', 'test_time']
                 ).to_csv(os.path.join(dest_dir, 'metrics_per_epoch.csv'), index=False)

    return None
