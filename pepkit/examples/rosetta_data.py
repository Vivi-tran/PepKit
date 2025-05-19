import importlib.resources as pkg_resources


def get_score_path(complex_id="complex_1"):
    """
    Return the path to a specific Rosetta docking score file.

    :param complex_id: The name of the complex subfolder (default "complex_1").
    :return: Pathlib.Path object pointing to the docking_scores.sc file.
    """
    return pkg_resources.files(__package__).joinpath(
        f"rosetta_test/refinement/{complex_id}/docking_scores.sc"
    )


def list_complexes():
    """
    List available complexes in rosetta_test.

    :return: List of complex IDs (folder names).
    """
    test_dir = pkg_resources.files(__package__).joinpath("rosetta_test")
    return [d.name for d in test_dir.iterdir() if d.is_dir()]


def get_refinement_path():
    """
    Return the path to the top-level 'refinement' directory containing
    all refined complexes.

    :return: Pathlib.Path object pointing to the 'rosetta_test/refinement' directory.
    """
    return pkg_resources.files(__package__).joinpath("rosetta_test/refinement")


def get_rosetta_ex_path():
    """
    Return the path to the top-level 'refinement' directory containing
    all refined complexes.

    :return: Pathlib.Path object pointing to the 'rosetta_test/refinement' directory.
    """
    return pkg_resources.files(__package__).joinpath("rosetta_test")
