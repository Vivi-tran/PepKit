import numpy as np
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from pepkit.metrics._common import normalize_minmax

# def normalize_minmax(arr):
#     arr = np.asarray(arr)
#     minv, maxv = np.min(arr), np.max(arr)
#     if maxv == minv:
#         return np.zeros_like(arr)
#     return (arr - minv) / (maxv - minv)


def pearson_corr(y_true, y_pred, normalize=False):
    """
    Pearson correlation coefficient (PCC).
    :param y_true: Ground-truth values.
    :param y_pred: Predicted values.
    :param normalize: Whether to min-max normalize y_true/y_pred to [0, 1].
    :return: PCC value.
    """
    if normalize:
        y_true = normalize_minmax(y_true)
        y_pred = normalize_minmax(y_pred)
    return pearsonr(y_true, y_pred)[0]


def spearman_corr(y_true, y_pred, normalize=False):
    """
    Spearman's rank correlation coefficient (SCC).
    :param y_true: Ground-truth values.
    :param y_pred: Predicted values.
    :param normalize: Whether to min-max normalize y_true/y_pred to [0, 1].
    :return: SCC value.
    """
    if normalize:
        y_true = normalize_minmax(y_true)
        y_pred = normalize_minmax(y_pred)
    return spearmanr(y_true, y_pred)[0]


def rmse(y_true, y_pred, normalize=False):
    """
    Root Mean Squared Error (RMSE).
    :param y_true: Ground-truth values.
    :param y_pred: Predicted values.
    :param normalize: Whether to min-max normalize y_true/y_pred to [0, 1].
    :return: RMSE value.
    """
    if normalize:
        y_true = normalize_minmax(y_true)
        y_pred = normalize_minmax(y_pred)
    return np.sqrt(mean_squared_error(y_true, y_pred))


def mae(y_true, y_pred, normalize=False):
    """
    Mean Absolute Error (MAE).
    :param y_true: Ground-truth values.
    :param y_pred: Predicted values.
    :param normalize: Whether to min-max normalize y_true/y_pred to [0, 1].
    :return: MAE value.
    """
    if normalize:
        y_true = normalize_minmax(y_true)
        y_pred = normalize_minmax(y_pred)
    return mean_absolute_error(y_true, y_pred)


def r2(y_true, y_pred, normalize=False):
    """
    R-squared (coefficient of determination).
    :param y_true: Ground-truth values.
    :param y_pred: Predicted values.
    :param normalize: Whether to min-max normalize y_true/y_pred to [0, 1].
    :return: R² value.
    """
    if normalize:
        y_true = normalize_minmax(y_true)
        y_pred = normalize_minmax(y_pred)
    return r2_score(y_true, y_pred)
