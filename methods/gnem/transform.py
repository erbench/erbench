import os
import pandas as pd


def transform_output(score_dicts, f1s, ps, rs, train_time, eval_time, results_per_epoch, dest_dir):

    # save predictions in predictions.csv
    l_id = []
    r_id = []
    probs = []
    labels = []
    for score_dict in score_dicts:
        for pair in score_dict.keys():
            l_id.append(pair[0])
            r_id.append(pair[1])
            probs.append(score_dict[pair][0]) # see test_GNEM calculate_f1
            labels.append(score_dict[pair][1])

    predictions = pd.DataFrame(data={'tableA_id': l_id, 'tableB_id': r_id, 'label':labels, 'prob_class1':probs})
    predictions = predictions.drop_duplicates()
    predictions.to_csv(os.path.join(dest_dir, 'predictions.csv'), index=False)

    # save evaluation metrics to metrics.csv
    pd.DataFrame({
        'f1': f1s,
        'precision': ps,
        'recall': rs,
        'train_time': [train_time] * len(f1s),
        'eval_time': [eval_time] * len(f1s),
    }).to_csv(os.path.join(dest_dir, 'metrics.csv'), index=False)

    pd.DataFrame(results_per_epoch,
                 columns=['epoch', 'f1', 'precision', 'recall', 'train_time', 'valid_time', 'test_time']
                 ).to_csv(os.path.join(dest_dir, 'metrics_per_epoch.csv'), index=False)
    return None
