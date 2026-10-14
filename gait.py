"""Gait chromosome decoder.

A chromosome is 72 genes: for each of the 24 joints, (amplitude, phase, offset).
Joint angle at frame f of n_frames (one full gait cycle):
    angle = offset + amplitude * sin(2*pi*f/n_frames + phase)
Layout: genes[0:24] amplitudes, genes[24:48] phases, genes[48:72] offsets.
"""
import numpy as np

N_JOINTS = 24
N_GENES = 3 * N_JOINTS
N_FRAMES = 300


def decode(genes, n_frames=N_FRAMES):
    """72 genes -> (n_frames, 24) array of joint angles in radians."""
    genes = np.asarray(genes, dtype=float)
    if genes.shape != (N_GENES,):
        raise ValueError(f"expected {N_GENES} genes, got shape {genes.shape}")
    amp, phase, offset = genes[:N_JOINTS], genes[N_JOINTS:2 * N_JOINTS], genes[2 * N_JOINTS:]
    t = 2.0 * np.pi * np.arange(n_frames) / n_frames
    return offset + amp * np.sin(t[:, None] + phase)
