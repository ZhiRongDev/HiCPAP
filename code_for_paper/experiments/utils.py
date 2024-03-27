import numpy as np
import pandas as pd
import logging
logging.basicConfig(format='%(message)s', level=logging.INFO)

def read_pearson(pearson: str, format="juicer") -> np.ndarray:
    """
    :param pearson: The text file path of `juicer_tools <https://github.com/aidenlab/juicer/wiki/Pearsons>`_  created Pearson matrix.
    :type pearson: str
    :return All `0` rows/columns removed pearson_np.
    :rtype: numpy.ndarray
    """
    if format == "juicer":
        pearson_df = pd.read_table(pearson, header=None, sep="\s+")
        pearson_np = pearson_df.values # Turn into numpy.ndarray
    elif format == "aiden_2009":
        pearson_df = pd.read_table(pearson, index_col=0, header=1, sep="\s+")
        pearson_np = pearson_df.values # Turn into numpy.ndarray

        diag = np.diag(pearson_np)
        diag_valid = diag != 0
        ixgrid = np.ix_(diag_valid, diag_valid) # Extract the valid sub-matrix.

        # Fill the all-zero rows/columns with `NaN`.
        length = len(pearson_np)
        tmp = np.full((length, length), np.nan) 
        tmp[ixgrid] = pearson_np[ixgrid] 
        pearson_np = tmp 

    return pearson_np

def flip_tracks(track1_np: np.ndarray, track2_np: np.ndarray):
    if len(track1_np) != len(track2_np):
        logging.info("The length of track1_np is different with track2_np")
        logging.info(f"Length of track1_np: {len(track1_np)}")
        logging.info(f"Length of track2_np: {len(track2_np)}")

    if np.corrcoef(track1_np[~np.isnan(track1_np)], track2_np[~np.isnan(track2_np)])[0][1] < 0:
        track2_np = -track2_np

    return track1_np, track2_np

def flip_track_gc(track_np: np.ndarray, gc_np: np.ndarray) -> np.ndarray:
    if len(track_np) != len(gc_np):
        logging.info("The length of track_np is different with gc_np")
        logging.info(f"Length of track_np: {len(track_np)}")
        logging.info(f"Length of gc_np: {len(gc_np)}")

    if np.mean(gc_np[track_np > 0]) < np.mean(gc_np[track_np < 0]):
        track_np = -track_np

    return track_np