"""Testing."""

from funcdim.crossval import make_components
from funcdim.crossval import reconstruct
from funcdim.funcdim import covdiag
from funcdim.funcdim import functional_dimensionality
from funcdim.funcdim import pre_proc
from funcdim.util import demo_data
import numpy as np
import output
from scipy.stats import pearsonr
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

    def test_covdiag(self):  # noqa:D102
        data = self.data[0][0]
        self.assertTrue(covdiag(data).shape == (self.nsubs, self.nsubs))

    def test_pre_proc(self):  # noqa:D102
        data = self.data[0]
        res = np.random.random(data.shape)
        self.assertTrue(pre_proc(data, res).shape == data.shape)

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
        self.data = demo_data(nvoxels=self.nvoxels, nsubs=self.nsubs,
                              functional_dims=5, nconditions=16)

    def test_covdiag(self):  # noqa:D102
        data = self.data[0][0]
        self.assertTrue(covdiag(data).shape == (self.nsubs, self.nsubs))

    def test_pre_proc(self):  # noqa:D102
        data = self.data[0]
        res = np.random.random(data.shape)
        self.assertTrue(pre_proc(data, res).shape == data.shape)

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


class TestCrossVal(unittest.TestCase):  # noqa:D101
    def setUp(self):  # noqa:D102
            # load the sample data.
        self.data = np.load('./demos/demo_data/sample_data.npy')
        # "data" has the shape (64, 16, 6, 20), containing beta values for 64
        # voxels, 16 conditions, 6 sessions, 20 subjects.
        self.nsubs = 20

        # Create a 4*4*4 mask (all True) for the 64 voxels.
        self.mask = np.ones((4, 4, 4), dtype='bool')

    def test_make_components(self):  # noqa:D102
        mc_u, mc_diag, mc_v = make_components(self.data)
        u, diag, v = np.linalg.svd(
            np.mean(self.data, axis=2), full_matrices=False)

        self.assertTrue(np.array_equal(mc_u, u))
        self.assertTrue(np.array_equal(mc_diag, np.diag(diag)))
        self.assertTrue(np.array_equal(mc_v.T, v))

    def test_reconstruct(self):  # noqa:D102
        data = self.data[0]
        n_beta, n_session = data.shape[1:]
        n_comp = n_beta - 1
        rmat = np.zeros((n_comp, n_session - 1, n_session))

        for i_test in range(n_session):
            # Remove the data for the ith session to produce test and
            # validation sets.
            data_val = np.delete(data, i_test, axis=2)

            for j_val in range(n_session - 1):
                # Remove the data for the jth session to produce training and
                # test sets.
                data_val_train = np.delete(data_val, j_val, axis=2)

                # Facorize the mean of the training set over all sessions.
                Uval, Sval, Vval = make_components(data_val_train)

                # Find the correlations between reconstructions of the training
                # set for each possible dimensionality and the test set.
                for comp in range(n_comp):
                    rmat[comp, j_val, i_test] = \
                        reconstruct(Uval, Sval, Vval, comp,
                                    data_val[:, :, j_val])
                    cor = rmat[comp, j_val, i_test]
                    s_red = np.copy(Sval)
                    # Set higher-dimensional components to zero.

                    s_red[:, comp + 1:] = 0.0
                    reconstruction = np.matmul(np.matmul(Uval, s_red), Vval.T)
                    correlation, _ = pearsonr(
                        reconstruction.ravel(), data_val[:, :, j_val].ravel())
                    self.assertEqual(cor, correlation)

if __name__ == '__main__':
    unittest.main()
