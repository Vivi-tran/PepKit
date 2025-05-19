import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Tuple, Optional

import MDAnalysis as mda
from MDAnalysis.topology.guessers import guess_types
from prolif.fingerprint import Fingerprint
from prolif.plotting.barcode import Barcode


__all__ = [
    "compute_interaction_fingerprint",
    "protein_interaction_frequency",
    "plot_interaction_fingerprint",
]


def compute_interaction_fingerprint(
    gro_path: str,
    traj_path: str,
    query_sel: Optional[str] = None,
    reference_sel: Optional[str] = None,
    threshold: float = 0.30,
    n_jobs: int = 4,
    vc_cutoff: int = 6,
    max_frames: Optional[int] = None,
    frame_stride: int = 1,
) -> pd.DataFrame:
    r"""
    Generate a fingerprint of intermolecular interactions and keep only the
    most persistent contacts.

    :param gro_path: Path to the GROMACS topology file (.gro).
    :type gro_path: str
    :param traj_path: Path to the GROMACS trajectory file (e.g., .xtc).
    :type traj_path: str
    :param query_sel: MDAnalysis selection string defining the ligand atoms.
                      If None, uses all atoms.
    :type query_sel: str or None
    :param reference_sel: MDAnalysis selection string defining the protein atoms.
                          If None, uses all atoms.
    :type reference_sel: str or None
    :param threshold: Fraction of frames an interaction must occur to retain it.
    :type threshold: float
    :param n_jobs: Number of parallel jobs for fingerprint calculation.
    :type n_jobs: int
    :param vc_cutoff: Distance cutoff (Å) to define an interaction.
    :type vc_cutoff: int
    :param max_frames: Maximum number of frames to analyze; None for all.
    :type max_frames: int or None
    :param frame_stride: Step between frames to sample (every Nth frame).
    :type frame_stride: int
    :return: DataFrame of filtered interactions with time in nanoseconds as index.
    :rtype: pandas.DataFrame
    """
    if not os.path.isfile(gro_path) or not os.path.isfile(traj_path):
        raise FileNotFoundError("Topology or trajectory file not found.")

    u = mda.Universe(gro_path, traj_path)
    u.add_TopologyAttr("elements", guess_types(u.atoms.names))

    lig = u.select_atoms(query_sel) if query_sel else u.atoms
    prot = u.select_atoms(reference_sel) if reference_sel else u.atoms

    total = len(u.trajectory)
    stop = min(max_frames, total) if max_frames else total
    traj = u.trajectory[0:stop:frame_stride]
    print(f"Analysing {len(traj)}/{total} frames (stride={frame_stride})…")

    fp = Fingerprint(vicinity_cutoff=vc_cutoff)
    fp.run(traj=traj, lig=lig, prot=prot, n_jobs=n_jobs)

    df = fp.to_dataframe().fillna(0)
    df = df.loc[:, df.mean() >= threshold]

    # Convert frame index to time in nanoseconds
    dt_ps = u.trajectory.dt  # picoseconds/frame
    df.index = df.index * dt_ps * frame_stride / 1000.0
    df.index.name = "time_ns"

    print(f"Kept {df.shape[1]} interactions ≥ {threshold:.0%} occurrence")
    return df


def protein_interaction_frequency(fp_df: pd.DataFrame) -> pd.DataFrame:
    r"""
    Collapse an interaction fingerprint to per-contact frequencies.

    Handles MultiIndex columns of two or more levels; the last two levels
    are assumed to be protein residue and interaction type respectively.
    If a third level (ligand) is present, it will be included.

    :param fp_df: Fingerprint DataFrame with MultiIndex columns.
    :type fp_df: pandas.DataFrame
    :return: DataFrame with columns ['ligand', 'protein', 'interaction', 'frequency']
    sorted by frequency.
    :rtype: pandas.DataFrame
    """
    # Compute frequency per contact
    freq_series = fp_df.astype(bool).mean(axis=0).rename("frequency")

    mi = freq_series.index
    nlv = mi.nlevels
    if nlv < 2:
        raise ValueError(
            "Fingerprint columns require at least two levels (protein, interaction)."
        )

    # Identify levels from the end
    # last level = interaction, penultimate = protein, antepenultimate
    # = ligand (if exists)
    lvl_inter = mi.names[-1] if mi.names[-1] else mi.levels[-1]
    lvl_prot = mi.names[-2] if mi.names[-2] else mi.levels[-2]

    if nlv >= 3:
        lvl_lig = mi.names[-3] if mi.names[-3] else mi.levels[-3]
        df_tidy = freq_series.reset_index().rename(
            columns={lvl_lig: "ligand", lvl_prot: "protein", lvl_inter: "interaction"}
        )[["ligand", "protein", "interaction", "frequency"]]
    else:
        # no ligand level: add placeholder
        df_tidy = freq_series.reset_index().rename(
            columns={lvl_prot: "protein", lvl_inter: "interaction"}
        )
        df_tidy["ligand"] = None
        df_tidy = df_tidy[["ligand", "protein", "interaction", "frequency"]]

    df_tidy.sort_values(["frequency", "protein"], ascending=[False, True], inplace=True)
    df_tidy.reset_index(drop=True, inplace=True)
    return df_tidy


def plot_interaction_fingerprint(
    fp_df: pd.DataFrame,
    save_path: Optional[str] = None,
    figsize: Tuple[int, int] = (8, 18),
    dpi: int = 300,
) -> None:
    r"""
    Display or save a barcode plot of an interaction fingerprint.

    Ensures a 'ligand' level exists for ProLIF Barcode by inserting
    a dummy level if needed.

    :param fp_df: Time-indexed DataFrame of interactions.
    :type fp_df: pandas.DataFrame
    :param save_path: Path to save the plot PNG; if None, the plot is shown.
    :type save_path: str or None
    :param figsize: Size of the figure (width, height) in inches.
    :type figsize: tuple[int, int]
    :param dpi: Dots per inch for figure resolution.
    :type dpi: int
    :return: None
    :rtype: None
    """
    sns.set_style("darkgrid")

    # Prepare DataFrame for Barcode: ensure MultiIndex has 'ligand'
    df_plot = fp_df.copy()
    cols = df_plot.columns
    if isinstance(cols, pd.MultiIndex):
        if "ligand" not in cols.names:
            # add dummy ligand level
            new_cols = pd.MultiIndex.from_tuples(
                [("LIG",) + tuple(col) for col in cols],
                names=["ligand"] + list(cols.names),
            )
            df_plot.columns = new_cols
    else:
        raise ValueError("DataFrame must have MultiIndex columns for plotting.")

    # Plot
    barcode = Barcode(df_plot)
    ax = barcode.display(dpi=dpi, xlabel=df_plot.index.name, figsize=figsize)
    ax.set_title("Interaction Fingerprint", fontsize=14, pad=10)
    ax.tick_params(axis="both", which="major", labelsize=8)

    fig = ax.get_figure()
    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight")
        print(f"Figure saved to {save_path}")
    else:
        plt.show()
    plt.close(fig)
