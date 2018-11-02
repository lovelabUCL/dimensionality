"""Testing."""

from funcdim.crossval import make_components
from funcdim.crossval import reconstruct
import numpy as np
from scipy.stats import pearsonr
import unittest


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
