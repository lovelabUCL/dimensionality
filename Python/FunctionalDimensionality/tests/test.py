"""Testing."""

from funcdim.funcdim import functional_dimensionality
from funcdim.util import demo_data
import numpy as np
import output
import unittest


class TestRealData(unittest.TestCase):  # noqa:D101
    def setUp(self):  # noqa:D102
        # load the sample data.
        self.data = np.load('./demos/demo_data/sample_data.npy')
        # "data" has the shape (64, 16, 6, 20), containing beta values for 64
        # voxels, 16 conditions, 6 sessions, 20 subjects.
        self.nsubs = 20

        # Create a 4*4*4 mask (all True) for the 64 voxels.
        self.mask = np.ones((4, 4, 4), dtype='bool')

    def test_full_keys(self):  # noqa:D102
        # Create an iterator over the 20 subjects.
        all_subjects = (self.data[:, :, :, i] for i in range(20))
        option = 'full'

        # Check the keys are identical.
        self.assertEqual(sorted(functional_dimensionality(
            all_subjects, 20, self.mask, option=option).keys()),
            sorted(output.dictionary_full.keys()))

    def test_full_values(self):  # noqa:D102
        # Create an iterator over the 20 subjects.
        all_subjects = (self.data[:, :, :, i] for i in range(20))
        option = 'full'

        # Loop through to compare the contents of both dictionaries:
        for (key, value) in functional_dimensionality(
                all_subjects, self.nsubs, self.mask, option=option).items():
            if key == 'subject_ID':
                self.assertTrue((value == output.dictionary_full[key]).all())
            else:
                self.assertTrue(np.allclose(value,
                                            output.dictionary_full[key]))

    def test_mean_keys(self):  # noqa:D102
        # Create an iterator over the 20 subjects.
        all_subjects = (self.data[:, :, :, i] for i in range(20))
        option = 'mean'

        # Check the keys are identical.
        self.assertEqual(sorted(functional_dimensionality(
            all_subjects, 20, self.mask, option=option).keys()),
            sorted(output.dictionary_mean.keys()))

    def test_mean_values(self):  # noqa:D102
        # Create an iterator over the 20 subjects.
        all_subjects = (self.data[:, :, :, i] for i in range(20))
        option = 'mean'

        # Loop through to compare the contents of both dictionaries:
        for (key, value) in functional_dimensionality(
                all_subjects, self.nsubs, self.mask, option=option).items():
            if key == 'subject_ID':
                self.assertTrue((value == output.dictionary_mean[key]).all())
            else:
                self.assertTrue(np.allclose(value,
                                            output.dictionary_mean[key]))


class TestSimData(unittest.TestCase):  # noqa:D101
    def setUp(self):  # noqa:D102
        self.nvoxels = 64
        self.nsubs = 20
        # Create a mask (all True) for nvoxels.
        mask_dim = int(np.round(np.power(self.nvoxels, 1 / 3)))
        self.mask = np.ones((mask_dim, mask_dim, mask_dim), dtype='bool')

    def test_full(self):  # noqa:D102
        for d in range(1, 10):
            # Get some randomly generated data with d dimensions as ground
            # truth:
            data = demo_data(nvoxels=self.nvoxels, nsubs=self.nsubs,
                             functional_dims=d, nconditions=16)
            # Create an iterator over the 20 subjects.
            all_subjects = (data[:, :, :, i] for i in range(20))
            option = 'full'

            self.assertEqual(d, functional_dimensionality(
                all_subjects, self.nsubs, self.mask, option=option)
                ['winning_model'].mean())

    def test_mean(self):  # noqa:D102
        for d in range(1, 10):
            # Get some randomly generated data with d dimensions as ground
            # truth:
            data = demo_data(nvoxels=self.nvoxels, nsubs=self.nsubs,
                             functional_dims=d, nconditions=16)
            # Create an iterator over the 20 subjects.
            all_subjects = (data[:, :, :, i] for i in range(20))
            option = 'mean'

            self.assertEqual(d, functional_dimensionality(
                all_subjects, self.nsubs, self.mask, option=option)
                ['winning_model'].mean())

if __name__ == '__main__':
    unittest.main()
