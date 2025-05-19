import numpy as np


def normalize_minmax(arr):
    """
    Min-max normalize an array to the range [0, 1].

    The function rescales the input array so that its minimum value becomes 0
    and its maximum value becomes 1. If all values are identical, returns an
    array of zeros.

    :param arr: Input array-like data (list, tuple, or numpy array).
    :type arr: array-like
    :return: Numpy array scaled to [0, 1].
    :rtype: numpy.ndarray

    Example
    -------
    >>> normalize_minmax([1, 2, 3])
    array([0. , 0.5, 1. ])
    >>> normalize_minmax([5, 5, 5])
    array([0., 0., 0.])
    """
    arr = np.asarray(arr)
    minv, maxv = np.min(arr), np.max(arr)
    if maxv == minv:
        return np.zeros_like(arr)
    return (arr - minv) / (maxv - minv)
