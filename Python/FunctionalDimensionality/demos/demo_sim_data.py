"""
Demo script using simulated data.

Call this demo from the ./Python/FunctionalDimensionality directory using:
python demos/demo_real_data.py
"""

from funcdim.funcdim import functional_dimensionality
from funcdim.util import demo_data
import numpy as np

# Get some randomly generated data with 4 dimensions as ground truth:
nvoxels = 64
nsubs = 20
data = demo_data(nvoxels=nvoxels, nsubs=nsubs, functional_dims=4)

# Create a mask (all True) for nvoxels.
mask_dim = int(np.round(np.power(nvoxels, 1 / 3)))
mask = np.ones((mask_dim, mask_dim, mask_dim), dtype='bool')

# Create an iterator over the 20 subjects.
all_subjects = (data[:, :, :, i] for i in range(nsubs))

# Find the dimensionality.
results = functional_dimensionality(all_subjects, nsubs, mask, option='full')

print(results['bestn'].mean())
