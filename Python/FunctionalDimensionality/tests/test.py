"""Testing."""

from funcdim.funcdim import functional_dimensionality
import numpy as np
import output
import unittest


class TestState(unittest.TestCase):  # noqa:D101

    def test_mean(self):  # noqa:D102
        # load the sample data.
        data = np.load('demo_data/sample_data.npy')
        # "data" has the shape (64, 16, 6, 20), containing beta values for 64
        # voxels, 16 conditions, 6 sessions, 20 subjects.

        # Create a 4*4*4 mask (all True) for the 64 voxels.
        mask = np.ones((4, 4, 4), dtype='bool')

        # Create an iterator over the 20 subjects.
        all_subjects = (data[:, :, :, i] for i in range(20))

        # Find the dimensionality.
        results = functional_dimensionality(
            all_subjects, 20, mask, option='mean')

        # Check the keys are identical.
        self.assertEqual(sorted(results.keys()),
                         sorted(output.dictionary_mean.keys()))

        # Loop through to compare the contents of both dictionaries:
        for (key, value) in results.items():
            self.assertTrue(np.allclose(value, output.dictionary_mean[key]))

    def test_full(self):  # noqa:D102
        # load the sample data.
        data = np.load('demo_data/sample_data.npy')
        # "data" has the shape (64, 16, 6, 20), containing beta values for 64
        # voxels, 16 conditions, 6 sessions, 20 subjects.

        # Create a 4*4*4 mask (all True) for the 64 voxels.
        mask = np.ones((4, 4, 4), dtype='bool')

        # Create an iterator over the 20 subjects.
        all_subjects = (data[:, :, :, i] for i in range(20))

        # Find the dimensionality.
        results = functional_dimensionality(
            all_subjects, 20, mask, option='full')

        # Check the keys are identical.
        self.assertEqual(sorted(results.keys()),
                         sorted(output.dictionary_full.keys()))

        # Loop through to compare the contents of both dictionaries:
        for (key, value) in results.items():
            self.assertTrue(np.allclose(value, output.dictionary_full[key]))

if __name__ == '__main__':
    unittest.main()
