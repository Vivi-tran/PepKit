import unittest
import numpy as np
import pepkit.metrics._regression as reg


class TestRegressionMetrics(unittest.TestCase):
    def setUp(self):
        self.y_true = np.array(
            [
                5.498509397602542,
                5.4129302889144695,
                5.249349691952619,
                4.78976015801953,
                4.20173265562076,
            ]
        )
        self.y_hat = np.array([7.467, 7.303, 7.369, 7.633, 7.52])

    def test_pearson_corr(self):
        val = reg.pearson_corr(self.y_true, self.y_hat)
        self.assertAlmostEqual(round(val, 3), round(-0.606, 3), places=3)

    def test_spearman_corr(self):
        val = reg.spearman_corr(self.y_true, self.y_hat)
        self.assertAlmostEqual(round(val, 2), round(-0.60, 2), places=2)

    def test_rmse(self):
        val = reg.rmse(self.y_true, self.y_hat)
        self.assertAlmostEqual(round(val, 3), round(2.491, 3), places=3)

    def test_mae(self):
        val = reg.mae(self.y_true, self.y_hat)
        self.assertAlmostEqual(round(val, 3), round(2.428, 3), places=3)

    def test_r2(self):
        val = reg.r2(self.y_true, self.y_hat)
        self.assertAlmostEqual(round(val, 2), round(-25.80, 2), places=2)

    def test_normalized(self):
        # Normalized results, just check they run and have valid type/range
        val = reg.pearson_corr(self.y_true, self.y_hat, normalize=True)
        self.assertTrue(-1 <= val <= 1)
        val = reg.spearman_corr(self.y_true, self.y_hat, normalize=True)
        self.assertTrue(-1 <= val <= 1)
        val = reg.rmse(self.y_true, self.y_hat, normalize=True)
        self.assertTrue(val >= 0)
        val = reg.mae(self.y_true, self.y_hat, normalize=True)
        self.assertTrue(val >= 0)
        val = reg.r2(self.y_true, self.y_hat, normalize=True)
        self.assertTrue(val <= 1)


if __name__ == "__main__":
    unittest.main()
