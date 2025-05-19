import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score
from pepkit.metrics._common import normalize_minmax

# def normalize_minmax(arr):
#     arr = np.asarray(arr)
#     minv, maxv = np.min(arr), np.max(arr)
#     if maxv == minv:
#         return np.zeros_like(arr)
#     return (arr - minv) / (maxv - minv)


def auc_score(y_true, y_pred_proba, normalize=False):
    """
    Area Under the ROC Curve (AUC).
    :param y_true: Binary labels.
    :param y_pred_proba: Predicted probabilities.
    :param normalize: If True, normalize y_pred_proba to [0, 1].
    :return: AUC score.
    """
    if normalize:
        y_pred_proba = normalize_minmax(y_pred_proba)
    return roc_auc_score(y_true, y_pred_proba)


def average_precision(y_true, y_pred_proba, normalize=False):
    """
    Average Precision (AP).
    :param y_true: Binary labels.
    :param y_pred_proba: Predicted probabilities.
    :param normalize: If True, normalize y_pred_proba to [0, 1].
    :return: AP score.
    """
    if normalize:
        y_pred_proba = normalize_minmax(y_pred_proba)
    return average_precision_score(y_true, y_pred_proba)


def enrichment_factor(y_true, y_pred_proba, top_percent=1, normalize=False):
    """
    Enrichment Factor (EF) at given % cutoff.
    :param y_true: Binary labels.
    :param y_pred_proba: Predicted probabilities.
    :param top_percent: Top % to consider (e.g., 1 for top 1%).
    :param normalize: If True, normalize y_pred_proba to [0, 1].
    :return: EF value.
    """
    y_true = np.asarray(y_true)
    y_pred_proba = np.asarray(y_pred_proba)
    if normalize:
        y_pred_proba = normalize_minmax(y_pred_proba)
    n = len(y_true)
    n_top = max(1, int(n * top_percent / 100))
    idx = np.argsort(y_pred_proba)[::-1]
    y_true_sorted = y_true[idx]
    n_active = np.sum(y_true)
    if n_active == 0:
        return np.nan
    top_hits = np.sum(y_true_sorted[:n_top])
    ef = (top_hits / n_top) / (n_active / n)
    return ef
