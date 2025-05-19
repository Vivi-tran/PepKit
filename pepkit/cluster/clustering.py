import numpy as np
from typing import List, Optional, Dict, Any
from sklearn.cluster import (
    KMeans,
    DBSCAN,
    AgglomerativeClustering,
    OPTICS,
    MeanShift,
    SpectralClustering,
    Birch,
)
from scipy.spatial.distance import pdist
from rdkit.ML.Cluster import Butina
from umap.umap_ import UMAP
import warnings


class Clustering:
    """
    Flexible clustering utility supporting multiple algorithms and distance metrics.

    Attempts to cluster input data using a specified algorithm:
        - If `algorithm` is 'kmeans', performs KMeans clustering (scikit-learn).
        - If 'dbscan', uses DBSCAN clustering.
        - If 'agglomerative', performs hierarchical clustering (AgglomerativeClustering).
        - If 'optics', uses the OPTICS density-based clustering.
        - If 'meanshift', applies MeanShift clustering.
        - If 'spectral', applies SpectralClustering.
        - If 'birch', uses the Birch clustering algorithm.
        - If 'butina', applies Butina clustering (for chemical similarity matrices).
        - If 'umap', reduces dimensionality via UMAP and clusters with KMeans.

    Most algorithms accept any metric supported by SciPy or scikit-learn,
    such as 'euclidean', 'cosine', 'manhattan', 'chebyshev', or 'minkowski'.
    UMAP supports its own metric choices.

    :param algorithm: Name of clustering algorithm to use. Supported values:
                     {'kmeans', 'dbscan', 'agglomerative', 'optics',
                      'meanshift', 'spectral', 'birch', 'butina', 'umap'}.
    :type algorithm: str
    :param distance: Distance metric or affinity for clustering.
                    Choices depend on the algorithm. For most, use
                    {'euclidean', 'cosine', 'manhattan', 'chebyshev', ...}.
    :type distance: str

    :raises ValueError: If an unsupported algorithm is requested.

    Example
    -------
    >>> clusterer = Clustering(algorithm='kmeans', distance='euclidean')
    >>> labels = clusterer.fit(data_array, params={'n_clusters': 3})
    >>> clusterer = Clustering(algorithm='umap', distance='cosine')
    >>> labels = clusterer.fit(data_array, params={'n_clusters': 5, 'n_neighbors': 10})

    Attributes
    ----------
    algorithm : str
        Name of the clustering algorithm used.
    distance : str
        Distance metric or affinity function.
    model_ : object
        The fitted clustering model (if applicable).
    labels_ : list of int
        Cluster labels for each input sample.
    embedding_ : np.ndarray or None
        If UMAP was used, stores the reduced embedding.

    Methods
    -------
    fit(data, params=None)
        Fit the clustering model to the data and return cluster labels.
    fit_predict(data, params=None)
        Alias for fit, provided for scikit-learn API compatibility.
    """

    SUPPORTED_ALGORITHMS = {
        "kmeans",
        "dbscan",
        "agglomerative",
        "optics",
        "meanshift",
        "spectral",
        "birch",
        "butina",
        "umap",
    }

    def __init__(self, algorithm: str = "kmeans", distance: str = "euclidean") -> None:
        """
        Initialize the clustering configuration.

        :param algorithm: Clustering method name (see class docstring for options).
        :type algorithm: str
        :param distance: Distance metric or affinity.
        :type distance: str
        :raises ValueError: If the algorithm is not supported.
        """
        algo = algorithm.lower()
        if algo not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(
                f"Unsupported algorithm '{algorithm}'. "
                f"Choose from {self.SUPPORTED_ALGORITHMS}."
            )
        self.algorithm = algo
        self.distance = distance
        self.model_: Any = None
        self.labels_: List[int] = []
        self.embedding_: Optional[np.ndarray] = None

    def fit(
        self, data: np.ndarray, params: Optional[Dict[str, Any]] = None
    ) -> List[int]:
        """
        Fit the selected clustering algorithm and return cluster labels.

        Attempts to cluster input data with the specified algorithm and parameters.
        See the class docstring for all supported algorithms and options.

        :param data: 2D array of shape (n_samples, n_features).
        :type data: np.ndarray
        :param params: Dictionary of algorithm-specific parameters. For example,
                      {'n_clusters': 3} for KMeans or Agglomerative;
                      {'eps': 0.5, 'min_samples': 5} for DBSCAN.
        :type params: dict, optional
        :raises ValueError: If algorithm or parameters are invalid.
        :return: Cluster labels for each input sample.
        :rtype: list of int

        Example
        -------
        >>> clusterer = Clustering(algorithm='dbscan', distance='cosine')
        >>> labels = clusterer.fit(my_data, params={'eps': 0.4, 'min_samples': 5})
        """
        if params is None:
            params = {}
        n_samples = data.shape[0]
        alg = self.algorithm

        if alg == "kmeans":
            n_clusters = params.get("n_clusters", 2)
            model = KMeans(n_clusters=n_clusters, random_state=0)
            labels = model.fit_predict(data)

        elif alg == "dbscan":
            eps = params.get("eps", 0.5)
            min_samples = params.get("min_samples", 5)
            model = DBSCAN(eps=eps, min_samples=min_samples, metric=self.distance)
            labels = model.fit_predict(data)

        elif alg == "agglomerative":
            n_clusters = params.get("n_clusters", 2)
            linkage = params.get("linkage", "average")
            model = AgglomerativeClustering(
                n_clusters=n_clusters, metric=self.distance, linkage=linkage
            )
            labels = model.fit_predict(data)

        elif alg == "optics":
            min_samples = params.get("min_samples", 5)
            max_eps = params.get("max_eps", np.inf)
            model = OPTICS(
                min_samples=min_samples, max_eps=max_eps, metric=self.distance
            )
            labels = model.fit_predict(data)

        elif alg == "meanshift":
            bandwidth = params.get("bandwidth", None)
            model = MeanShift(bandwidth=bandwidth)
            labels = model.fit_predict(data)

        elif alg == "spectral":
            n_clusters = params.get("n_clusters", 2)
            affinity_val = params.get("affinity", None)
            valid_affinities = {
                "precomputed",
                "cosine",
                "chi2",
                "linear",
                "polynomial",
                "additive_chi2",
                "sigmoid",
                "nearest_neighbors",
                "rbf",
                "precomputed_nearest_neighbors",
                "laplacian",
                "poly",
            }
            if affinity_val is None:
                affinity_val = (
                    self.distance if self.distance in valid_affinities else "rbf"
                )
            if affinity_val not in valid_affinities:
                warnings.warn(
                    f"Affinity '{affinity_val}' is not valid for SpectralClustering; "
                    + "falling back to 'rbf'."
                )
                affinity_val = "rbf"
            sc_kwargs: Dict[str, Any] = {
                "n_clusters": n_clusters,
                "affinity": affinity_val,
                "assign_labels": "kmeans",
            }
            gamma = params.get("gamma")
            if affinity_val == "rbf" and gamma is not None:
                sc_kwargs["gamma"] = gamma
            model = SpectralClustering(**sc_kwargs)
            labels = model.fit_predict(data)

        elif alg == "birch":
            threshold = params.get("threshold", 0.5)
            n_clusters = params.get("n_clusters")
            model = Birch(threshold=threshold, n_clusters=n_clusters)
            labels = model.fit_predict(data)

        elif alg == "butina":
            dists = pdist(data, metric=self.distance)
            cutoff = params.get("cutoff", 0.7)
            clusters = Butina.ClusterData(
                list(dists), n_samples, cutoff, isDistData=True
            )
            labels = [-1] * n_samples
            for cid, cluster in enumerate(clusters):
                for idx in cluster:
                    labels[idx] = cid
            labels = np.array(labels)
            model = None

        elif alg == "umap":
            n_neighbors = params.get("n_neighbors", 15)
            min_dist = params.get("min_dist", 0.1)
            n_components = params.get("n_components", 2)
            umap_model = UMAP(
                n_neighbors=n_neighbors,
                min_dist=min_dist,
                n_components=n_components,
                metric=self.distance,
                random_state=0,
            )
            embedding = umap_model.fit_transform(data)
            n_clusters = params.get("n_clusters", 2)
            model = KMeans(n_clusters=n_clusters, random_state=0)
            labels = model.fit_predict(embedding)
            self.embedding_ = embedding
            self.model_ = (umap_model, model)

        else:
            raise ValueError(f"Unsupported algorithm: {alg}")

        # store fitted model and labels
        if alg != "umap":
            self.model_ = model
        self.labels_ = list(labels)
        return self.labels_

    def fit_predict(
        self, data: np.ndarray, params: Optional[Dict[str, Any]] = None
    ) -> List[int]:
        """
        Shorthand for `fit` to mimic scikit-learn API.

        :param data: 2D array of samples.
        :type data: np.ndarray
        :param params: Algorithm-specific keyword arguments.
        :type params: dict, optional
        :return: Cluster labels per sample.
        :rtype: list of int
        """
        return self.fit(data, params)

    def __repr__(self) -> str:
        return f"<Clustering algorithm='{self.algorithm}' distance='{self.distance}'>"
