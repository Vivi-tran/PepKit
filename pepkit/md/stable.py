import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Tuple, Optional
from joblib import Parallel, delayed
import MDAnalysis as mda
from MDAnalysis.analysis import align, rms


__all__ = [
    "compute_rmsf",
    "plot_rmsf",
    "compute_rmsd",
    "plot_rmsd",
]


def compute_rmsf(
    gro: str,
    traj: str,
    res_sel: str = "protein and name CA",
    ref_frame: int = 0,
    shift: float = 0.0,
    max_frames: Optional[int] = None,
    frame_stride: int = 1,
    do_align: bool = True,
    verbose: bool = False,
    n_jobs: int = 1,
) -> pd.DataFrame:
    r"""
    Compute per-residue RMSF efficiently, with optional alignment, verbosity,
    and parallel loading.

    :param gro: Path to GROMACS .gro file.
    :param traj: Path to GROMACS trajectory (e.g., .xtc).
    :param res_sel: MDAnalysis atom selection string (e.g., 'protein and name CA').
    :param ref_frame: Frame index to use as reference for alignment and start.
    :param shift: Value to add to residue IDs (offset).
    :param max_frames: Max frames to process; None means all available after ref_frame.
    :param frame_stride: Step size for frame sampling.
    :param do_align: Whether to align each frame to the reference
    before computing fluctuations.
    :param verbose: If True, prints progress information.
    :param n_jobs: Number of parallel workers to load frames (requires joblib).
    :return: DataFrame with columns ['resid', 'rmsf'].
    """

    # Load universe and select atoms
    u = mda.Universe(gro, traj)
    atoms = u.select_atoms(res_sel)

    # Determine frame indices
    total_frames = len(u.trajectory)
    start = ref_frame
    stop = min(start + max_frames, total_frames) if max_frames else total_frames
    frame_indices = list(range(start, stop, frame_stride))
    n_frames = len(frame_indices)
    if n_frames == 0:
        raise ValueError(
            "No frames selected: check ref_frame, max_frames, and frame_stride."
        )

    # Align trajectory if requested
    if do_align:
        if verbose:
            print(f"Aligning trajectory to frame {ref_frame}...")
        ref = u.copy()
        ref.trajectory[ref_frame]
        align.AlignTraj(u, ref, select=res_sel, in_memory=False).run()

    # Frame loading function
    def load_frame(idx, count=None):
        u.trajectory[idx]
        positions = atoms.positions.copy()
        if verbose and count is not None:
            print(f"Loaded frame {count}/{n_frames} (index {idx})")
        return positions

    # Load positions list (parallel or serial)
    if n_jobs != 1:
        if verbose:
            print(f"Loading {n_frames} frames in parallel with {n_jobs} jobs...")
        pos_list = Parallel(n_jobs=n_jobs)(
            delayed(load_frame)(idx, i + 1) for i, idx in enumerate(frame_indices)
        )
    else:
        pos_list = []
        for i, idx in enumerate(frame_indices):
            pos = load_frame(idx, i + 1) if verbose else load_frame(idx)
            pos_list.append(pos)

    # Stack positions into array
    positions = np.stack(pos_list, axis=0)  # (n_frames, n_atoms, 3)

    # Compute RMSF per atom
    mean_pos = positions.mean(axis=0)
    diffs = positions - mean_pos
    rmsf_per_atom = np.sqrt((diffs**2).sum(axis=2).mean(axis=0))

    # Build DataFrame
    df = pd.DataFrame({"resid": atoms.resids + shift, "rmsf": rmsf_per_atom})
    return df


def plot_rmsf(
    df_rmsf: pd.DataFrame,
    highlight_region: Optional[Tuple[int, int]] = None,
    show_top: int = 0,
    save_path: Optional[str] = None,
    figsize: Tuple[int, int] = (12, 6),
    dpi: int = 300,
    bbox_to_anchor=(0.85, 0.05),
) -> None:
    r"""
    Enhanced RMSF plot with optional highlighted region,
    top-residue annotations, and bottom-centered legend.

    :param df_rmsf: DataFrame with columns ['resid', 'rmsf'].
    :param highlight_region: Tuple (start, end) to highlight a residue range.
    :param show_top: Number of top RMSF residues to annotate.
    :param save_path: File path to save the plot; if None, shows interactively.
    :param figsize: Figure size in inches.
    :param dpi: Resolution for saving.
    """
    sns.set_style("whitegrid")
    sns.set_context("talk", font_scale=1.1)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi, constrained_layout=True)
    # Primary line
    sns.lineplot(
        x="resid", y="rmsf", data=df_rmsf, ax=ax, marker="o", linewidth=2, label="RMSF"
    )
    # Highlight region
    if highlight_region:
        ax.axvspan(
            highlight_region[0],
            highlight_region[1],
            color="yellow",
            alpha=0.3,
            label="Highlighted Region",
        )
    # Annotate top RMSF peaks
    if show_top > 0:
        top_df = df_rmsf.nlargest(show_top, "rmsf")
        for _, row in top_df.iterrows():
            ax.annotate(
                f"{int(row['resid'])}: {row['rmsf']:.2f}",
                xy=(row["resid"], row["rmsf"]),
                xytext=(0, 5),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
                arrowprops=dict(arrowstyle="->", color="gray", lw=0.5),
            )
    # Labels and title
    ax.set_xlabel("Residue ID")
    ax.set_ylabel("RMSF (Å)")
    ax.set_title("RMSF per Residue", fontsize=24, weight="bold")
    # Clean up
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.grid(which="major", linestyle="--", alpha=0.6)
    # Legend bottom center
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        handles,
        labels,
        loc="lower left",
        bbox_to_anchor=bbox_to_anchor,
        ncol=len(labels),
        borderaxespad=0,
    )

    if save_path:
        fig.savefig(save_path, bbox_inches="tight", dpi=dpi)
    else:
        plt.show()
    plt.close()


def compute_rmsd(
    gro: str,
    traj: str,
    atom_sel: str = "protein and backbone",
    ref_frame: int = 0,
    time_divisor: float = 1000.0,
) -> pd.DataFrame:
    r"""
    Compute RMSD over time for specified atom selection, optionally
    starting from a given reference frame.

    :param gro: Path to GROMACS .gro file.
    :param traj: Path to trajectory file (e.g., .xtc).
    :param atom_sel: MDAnalysis selection string for RMSD calculation.
    :param ref_frame: Reference frame index; also number of initial frames to skip.
    :param time_divisor: Factor to convert raw time units (ps to ns via 1000).
    :return: DataFrame with columns ['time', 'rmsd'].
    """
    # Load universe and select atoms
    u = mda.Universe(gro, traj)
    sel = f"{atom_sel}"

    # Set up RMSD analysis: reference frame and select atoms
    rmsd_analysis = rms.RMSD(u, select=sel, ref_frame=ref_frame)

    # Run RMSD: start analysis at ref_frame to skip prior frames
    rmsd_analysis.run(start=ref_frame)

    # Extract results: columns are [frame_index, time, rmsd]
    results = rmsd_analysis.results.rmsd

    # Convert time to desired units and build DataFrame
    times = results[:, 1] / time_divisor
    rmsd_values = results[:, 2]
    df = pd.DataFrame({"time": times, "rmsd": rmsd_values})
    return df


def plot_rmsd(
    df_rmsd: pd.DataFrame,
    save_path: Optional[str] = None,
    figsize: Tuple[int, int] = (12, 6),
    dpi: int = 300,
    smooth_window: int = 50,
    smooth: bool = True,
) -> None:
    r"""
    Enhanced RMSD plot with optional smoothing, shaded variability,
    and bottom-centered legend without shrinking axes.

    :param df_rmsd: DataFrame with columns ['time', 'rmsd'].
    :param save_path: File path to save the plot; if None, shows interactively.
    :param figsize: Size of the figure in inches.
    :param dpi: Resolution for saving.
    :param smooth_window: Window size for rolling average smoothing.
    :param smooth: Whether to apply smoothing and variability shading.
    """
    # Set visual style and context
    sns.set_style("whitegrid")
    sns.set_context("talk", font_scale=1.1)

    # Prepare data
    df = df_rmsd.copy()
    if smooth:
        df["rmsd_smooth"] = (
            df["rmsd"].rolling(window=smooth_window, min_periods=1).mean()
        )
        df["rmsd_std"] = (
            df["rmsd"].rolling(window=smooth_window, min_periods=1).std().fillna(0)
        )

    # Create figure and axes with constrained layout to allocate legend space
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi, constrained_layout=True)

    # Plot raw trace
    sns.lineplot(
        x="time", y="rmsd", data=df, ax=ax, label="Raw RMSD", alpha=0.3, linewidth=1
    )

    # Plot smoothed trace and variability if enabled
    if smooth:
        sns.lineplot(
            x="time",
            y="rmsd_smooth",
            data=df,
            ax=ax,
            label=f"Smoothed (window={smooth_window})",
            linewidth=2.5,
        )
        ax.fill_between(
            df["time"],
            df["rmsd_smooth"] - df["rmsd_std"],
            df["rmsd_smooth"] + df["rmsd_std"],
            alpha=0.2,
            label="±1σ",
        )

        # Highlight and annotate min/max on smooth curve
        idx_min = df["rmsd_smooth"].idxmin()
        idx_max = df["rmsd_smooth"].idxmax()
        t_min, r_min = df.loc[idx_min, ["time", "rmsd_smooth"]]
        t_max, r_max = df.loc[idx_max, ["time", "rmsd_smooth"]]
        ax.scatter([t_min, t_max], [r_min, r_max], s=80, color="red", zorder=5)
        ax.annotate(
            f"Min: {r_min:.2f} Å",
            xy=(t_min, r_min),
            xytext=(t_min, r_min + df["rmsd_std"].max() * 1.5),
            arrowprops=dict(arrowstyle="->", color="red"),
            fontsize=10,
        )
        ax.annotate(
            f"Max: {r_max:.2f} Å",
            xy=(t_max, r_max),
            xytext=(t_max, r_max + df["rmsd_std"].max() * 1.5),
            arrowprops=dict(arrowstyle="->", color="red"),
            fontsize=10,
        )

    # Labels and title
    ax.set_xlabel("Time (ns)")
    ax.set_ylabel("RMSD (Å)")
    ax.set_title("RMSD over Time", fontsize=24, weight="bold")

    # Improve spines and grid
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.grid(which="major", linestyle="--", alpha=0.6)

    # Bottom-centered legend in one row without shrinking the axes
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.4),  # slight offset
        ncol=len(labels),
        borderaxespad=0,
    )

    # Save or show (no tight_layout needed thanks to constrained_layout)
    if save_path:
        fig.savefig(save_path, bbox_inches="tight", dpi=dpi)
    else:
        plt.show()
    plt.close()
