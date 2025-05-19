import unittest
import numpy as np
import pepkit.metrics._classification as clf


class TestClassificationMetrics(unittest.TestCase):
    def setUp(self):
        self.y_true = np.array([1, 1, 1, 0, 0])
        self.y_pred = np.array([0.4969697, 0.0, 0.2, 1.0, 0.65757576])

    def test_auc_score(self):
        val = clf.auc_score(self.y_true, self.y_pred)
        # Actual computed value is 0.0 for this example
        self.assertAlmostEqual(val, 0.0, places=4)

    def test_average_precision(self):
        val = clf.average_precision(self.y_true, self.y_pred)
        # Actual computed value is about 0.4778
        self.assertAlmostEqual(round(val, 4), round(0.4778, 4), places=4)

    def test_enrichment_factor_1(self):
        val = clf.enrichment_factor(self.y_true, self.y_pred, top_percent=1)
        self.assertTrue(val >= 0 or np.isnan(val))

    def test_enrichment_factor_20(self):
        val = clf.enrichment_factor(self.y_true, self.y_pred, top_percent=20)
        self.assertTrue(val >= 0 or np.isnan(val))

    def test_normalize_auc(self):
        val = clf.auc_score(self.y_true, self.y_pred, normalize=True)
        self.assertTrue(0 <= val <= 1)

    def test_normalize_ap(self):
        val = clf.average_precision(self.y_true, self.y_pred, normalize=True)
        self.assertTrue(0 <= val <= 1)

    def test_normalize_ef(self):
        val = clf.enrichment_factor(
            self.y_true, self.y_pred, top_percent=1, normalize=True
        )
        self.assertTrue(val >= 0 or np.isnan(val))


if __name__ == "__main__":
    unittest.main()
