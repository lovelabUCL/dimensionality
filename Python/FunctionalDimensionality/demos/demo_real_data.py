"""
Demo script using real data.

Call this demo from the ./Python/FunctionalDimensionality directory using:
python demos/demo_real_data.py
"""

from funcdim.funcdim import functional_dimensionality
import numpy as np
import pandas as pd

# load the sample data.
data = np.load('./demos/demo_data/sample_data.npy')
# "data" has the shape (64, 16, 6, 20), containing beta values for 64 voxels,
# 16 conditions, 6 sessions, 20 subjects.
nsubs = 20

# Create the subject IDs.
subject_IDs = [str(i) for i in range(1, nsubs + 1)]

# Create a 4*4*4 mask (all True) for the 64 voxels.
mask = np.ones((4, 4, 4), dtype='bool')

# Create an iterator over the 20 subjects.
all_subjects = (data[:, :, :, i] for i in range(nsubs))

# Find the dimensionality.
results = functional_dimensionality(all_subjects, nsubs, mask,
                                    subject_IDs=subject_IDs, option='mean')

# Put the output results into a dataframe and save as a CSV file.
df = pd.DataFrame.from_dict(results)
df.to_csv('./demos/demo_data/demo_real_data_output.csv')

# Show the median dimensionality:
print(df['winning_model'].median())
