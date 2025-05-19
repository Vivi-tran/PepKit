from typing import Dict, Any
import pandas as pd
from ._regression import pearson_corr, spearman_corr, rmse, mae, r2
from ._classification import auc_score, average_precision, enrichment_factor


def compute_regression_metrics(y_true, y_pred, normalize=False) -> Dict[str, Any]:
    """
    Compute common regression metrics between y_true and y_pred.

    :param y_true: Ground-truth continuous values.
    :param y_pred: Predicted continuous values.
    :param normalize: Whether to min-max normalize inputs to [0, 1].
    :return: Dict of all regression metrics.
    """
    return {
        "PCC": pearson_corr(y_true, y_pred, normalize=normalize),
        "SCC": spearman_corr(y_true, y_pred, normalize=normalize),
        "RMSE": rmse(y_true, y_pred, normalize=normalize),
        "MAE": mae(y_true, y_pred, normalize=normalize),
        "R2": r2(y_true, y_pred, normalize=normalize),
    }


def compute_classification_metrics(
    y_true, y_pred_proba, top_percents=[1, 5, 10], normalize=False
) -> Dict[str, Any]:
    """
    Compute common classification metrics for binary y_true and
    probabilistic y_pred_proba.

    :param y_true: Binary true labels (0 or 1).
    :param y_pred_proba: Predicted probabilities for the positive class.
    :param top_percents: List of top-% cutoffs for enrichment factor (default: [1, 5, 10])
    :param normalize: Whether to min-max normalize probabilities to [0, 1].
    :return: Dict of all classification metrics.
    """
    out = {
        "AUC": auc_score(y_true, y_pred_proba, normalize=normalize),
        "AP": average_precision(y_true, y_pred_proba, normalize=normalize),
    }
    for pct in top_percents:
        out[f"EF{pct}"] = enrichment_factor(
            y_true, y_pred_proba, top_percent=pct, normalize=normalize
        )
    return out


def compute_metrics_from_dataframe(
    df: pd.DataFrame,
    ground_truth_key: str,
    pred_key: str,
    task: str = "regression",
    normalize: bool = False,
    top_percents: list = [1, 5, 10],
):
    """
    Compute regression or classification metrics from a DataFrame.

    :param df: DataFrame with at least two columns.
    :param ground_truth_key: Column name for ground truth values (y or y_true).
    :param pred_key: Column name for predictions (y_hat or y_pred).
    :param task: "regression" or "classification".
    :param normalize: Whether to min-max normalize inputs.
    :param top_percents: For classification, list of EF cutoffs.
    :return: Dictionary of metrics.
    """
    y_true = df[ground_truth_key].values
    y_pred = df[pred_key].values
    if task == "regression":
        return compute_regression_metrics(y_true, y_pred, normalize=normalize)
    elif task == "classification":
        return compute_classification_metrics(
            y_true, y_pred, top_percents=top_percents, normalize=normalize
        )
    else:
        raise ValueError(
            f"Unknown task type '{task}'. Choose 'regression' or 'classification'."
        )
