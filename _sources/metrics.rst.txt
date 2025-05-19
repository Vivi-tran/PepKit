Metrics
=======

The `pepkit.metrics` package provides a standard interface for evaluating regression and classification models on peptide datasets. 

Regression
----------
**Regression metrics** for tasks such as continuous affinity prediction or quantitative property estimation. This submodule includes:

- `pearson_corr`: Pearson correlation coefficient between ground truth and predicted values.
- `spearman_corr`: Spearman rank correlation coefficient.
- `rmse`: Root mean squared error.
- `mae`: Mean absolute error.
- `r2`: Coefficient of determination (R² score).

*Example:*

.. code-block:: python

    import numpy as np
    from pepkit.metrics import _regression as reg

    y_true = np.array([5.5, 5.4, 5.2, 4.8, 4.2])
    y_pred = np.array([7.467, 7.303, 7.369, 7.633, 7.52])
    print("Pearson:", reg.pearson_corr(y_true, y_pred))
    print("Spearman:", reg.spearman_corr(y_true, y_pred))
    print("RMSE:", reg.rmse(y_true, y_pred))
    print("MAE:", reg.mae(y_true, y_pred))
    print("R2:", reg.r2(y_true, y_pred))

Classification
--------------
**Classification metrics** for evaluating binary/probabilistic peptide models, e.g., binder vs. non-binder classification. This submodule includes:

- `auc_score`: Area under the ROC curve (AUC).
- `average_precision`: Area under the precision-recall curve (AP).
- `enrichment_factor`: Early enrichment metric (EF) for virtual screening, with customizable cutoffs.

*Example:*

.. code-block:: python

    import numpy as np
    from pepkit.metrics import _classification as clf

    y_true = np.array([1, 1, 1, 0, 0])
    y_pred = np.array([0.5, 0.0, 0.2, 1.0, 0.65])
    print("AUC:", clf.auc_score(y_true, y_pred))
    print("Average precision:", clf.average_precision(y_true, y_pred))
    print("Enrichment factor @ 20%:", clf.enrichment_factor(y_true, y_pred, top_percent=20))

Data Process
------------
**Utility functions** for batch metric computation and DataFrame workflows. Useful for applying all relevant metrics in a single call and for integration in ML pipelines.

- `compute_regression_metrics`: Returns a dictionary of regression metrics (PCC, SCC, RMSE, MAE, R2).
- `compute_classification_metrics`: Returns a dictionary of classification metrics (AUC, AP, and EF at several cutoffs).
- `compute_metrics_from_dataframe`: Computes metrics from DataFrame columns for either regression or classification tasks.

*Example:*

.. code-block:: python

    import numpy as np
    import pandas as pd
    from pepkit.metrics._base import (
        compute_regression_metrics, compute_classification_metrics, compute_metrics_from_dataframe
    )

    y_true = np.array([5.5, 5.4, 5.2, 4.8, 4.2])
    y_pred = np.array([7.467, 7.303, 7.369, 7.633, 7.52])
    # Compute all regression metrics
    reg_metrics = compute_regression_metrics(y_true, y_pred)
    print(reg_metrics)

    # Classification example
    y_true_clf = np.array([1, 1, 0, 0, 1])
    y_pred_proba = np.array([0.7, 0.3, 0.2, 0.8, 0.6])
    clf_metrics = compute_classification_metrics(y_true_clf, y_pred_proba)
    print(clf_metrics)

    # DataFrame usage
    df = pd.DataFrame({"y_true": y_true, "y_pred": y_pred})
    results = compute_metrics_from_dataframe(df, ground_truth_key="y_true", pred_key="y_pred", task="regression")
    print(results)



Testing and API Reference
-------------------------

See ``test/metrics/`` for complete unittests and example-based validation.

Full function and class documentation: see `API Reference <https://Vivi-tran.github.io/PepKit/api.html>`_

