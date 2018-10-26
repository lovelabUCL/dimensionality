#!/usr/bin/env python3

import sys
sys.path.insert(0, '../')
from funcdim.funcdim import functional_dimensionality
import numpy as np

ndims = 16
functional_dims = 4
nvoxels = 64 #has to be a power of 3
nconditions = 16
nruns = 6
nsubs = 20

# "data" has the shape (nvoxels, nconditions, nruns, nsubs), containing "beta" values for nvoxels,
data = np.random.multivariate_normal(np.zeros((ndims,)),np.eye(ndims), size=(nvoxels))
data[:,functional_dims:] = np.zeros((data[:,functional_dims:].shape))
data = data.reshape((nvoxels, nconditions, 1))
data = np.tile(data,(nruns))
data = data.reshape((nvoxels, nconditions, nruns, 1))
data = np.tile(data,(nsubs))

# Create a mask (all True) for nvoxels.
mask_dim = int(np.round(np.power(nvoxels,1/3)))
mask = np.ones((mask_dim, mask_dim, mask_dim), dtype='bool')

# Create an iterator over the 20 subjects.
all_subjects = (data[:, :, :, i] for i in range(nsubs))

# Find the dimensionality.
results = functional_dimensionality(all_subjects, nsubs, mask, option='full')

#print(results['bestn'])
print(np.mean(results['bestn']))
