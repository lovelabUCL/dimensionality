"""
Demo script using real data.

Call this demo from the ./Python/FunctionalDimensionality directory using:
python demos/demo_real_data.py
"""
from funcdim.funcdim import functional_dimensionality

import numpy as np
# import random

# load the sample data.
data = np.load('./demos/demo_data/sample_data.npy')
# "data" has the shape (64, 16, 6, 20), containing beta values for 64 voxels,
# 16 conditions, 6 sessions, 20 subjects.

# Create a 4*4*4 mask (all True) for the 64 voxels.
mask = np.ones((4, 4, 4), dtype='bool')

# Create an iterator over the 20 subjects.
all_subjects = (data[:, :, :, i] for i in range(20))

# Find the dimensionality.
results = functional_dimensionality(all_subjects, 20, mask, option='full')

print(results['bestn'].mean())
