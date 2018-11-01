"""
Demo script using simulated data.

Call this demo from the ./Python/FunctionalDimensionality directory using:
python demos/demo_sim_data.py
"""

from funcdim.funcdim import functional_dimensionality
from funcdim.util import demo_data
import numpy as np
import pandas as pd

# Get some randomly generated data with 4 dimensions as ground truth:
nvoxels = 64
nsubs = 20

# Create the subject IDs.
subject_IDs = [str(i) for i in range(1, nsubs + 1)]

# Create the random demo data.
data = demo_data(nvoxels=nvoxels, nsubs=nsubs, functional_dims=4)

# Create a mask (all True) for nvoxels.
mask_dim = int(np.round(np.power(nvoxels, 1 / 3)))
mask = np.ones((mask_dim, mask_dim, mask_dim), dtype='bool')

# Create an iterator over the 20 subjects.
all_subjects = (data[:, :, :, i] for i in range(nsubs))

# Find the dimensionality.
results = functional_dimensionality(all_subjects, nsubs, mask,
                                    subject_IDs=subject_IDs)

# Put the output results into a dataframe and save as a CSV file.
df = pd.DataFrame.from_dict(results)
df.to_csv('./demos/demo_data/demo_sim_data_output.csv')

# Show the median dimensionality:
print(df['winning_model'].median())
