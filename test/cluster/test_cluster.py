import unittest
import numpy as np

from pepkit.cluster.clustering import Clustering


class TestClustering(unittest.TestCase):
    def setUp(self):
        # Two well-separated Gaussian blobs for algorithms expecting clusters
        np.random.seed(0)
        blob1 = np.random.randn(50, 2) * 0.1 + np.array([0, 0])
        blob2 = np.random.randn(50, 2) * 0.1 + np.array([5, 5])
        self.X_two_blobs = np.vstack([blob1, blob2])
        # Random data for general-purpose algorithms
        self.X_random = np.random.rand(100, 5)

    def test_kmeans(self):
        clusterer = Clustering(algorithm="kmeans")
        labels = clusterer.fit_predict(self.X_two_blobs, params={"n_clusters": 2})
        # Check output length and cluster count
        self.assertEqual(len(labels), self.X_two_blobs.shape[0])
        self.assertEqual(len(set(labels)), 2)

    def test_dbscan(self):
        clusterer = Clustering(algorithm="dbscan", distance="euclidean")
        labels = clusterer.fit_predict(
            self.X_two_blobs, params={"eps": 0.5, "min_samples": 5}
        )
        self.assertEqual(len(labels), self.X_two_blobs.shape[0])
        # Ensure at least one point is assigned to a cluster (not all noise)
        self.assertTrue(any(label != -1 for label in labels))

    def test_agglomerative(self):
        clusterer = Clustering(algorithm="agglomerative", distance="euclidean")
        labels = clusterer.fit_predict(
            self.X_two_blobs, params={"n_clusters": 2, "linkage": "average"}
        )
        self.assertEqual(len(labels), self.X_two_blobs.shape[0])
        self.assertEqual(len(set(labels)), 2)

    def test_optics(self):
        clusterer = Clustering(algorithm="optics", distance="euclidean")
        labels = clusterer.fit_predict(
            self.X_two_blobs, params={"min_samples": 5, "max_eps": np.inf}
        )
        self.assertEqual(len(labels), self.X_two_blobs.shape[0])

    def test_meanshift(self):
        clusterer = Clustering(algorithm="meanshift")
        labels = clusterer.fit_predict(self.X_random, params={"bandwidth": 2})
        self.assertEqual(len(labels), self.X_random.shape[0])

    def test_spectral(self):
        clusterer = Clustering(algorithm="spectral", distance="euclidean")
        labels = clusterer.fit_predict(self.X_two_blobs, params={"n_clusters": 2})
        self.assertEqual(len(labels), self.X_two_blobs.shape[0])
        self.assertEqual(len(set(labels)), 2)

    def test_birch(self):
        clusterer = Clustering(algorithm="birch")
        labels = clusterer.fit_predict(
            self.X_two_blobs, params={"threshold": 1.5, "n_clusters": 2}
        )
        self.assertEqual(len(labels), self.X_two_blobs.shape[0])

    def test_butina(self):
        clusterer = Clustering(algorithm="butina")
        labels = clusterer.fit_predict(self.X_random, params={"cutoff": 0.5})
        self.assertEqual(len(labels), self.X_random.shape[0])

    def test_umap(self):
        clusterer = Clustering(algorithm="umap", distance="euclidean")
        labels = clusterer.fit_predict(
            self.X_random,
            params={
                "n_neighbors": 10,
                "min_dist": 0.2,
                "n_components": 2,
                "n_clusters": 3,
            },
        )
        self.assertEqual(len(labels), self.X_random.shape[0])
        # Ensure embedding and pipeline are stored
        self.assertIsNotNone(clusterer.embedding_)
        umap_model, kmeans_model = clusterer.model_
        self.assertEqual(kmeans_model.n_clusters, 3)


if __name__ == "__main__":
    unittest.main()
