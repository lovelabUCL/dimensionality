"""Copyright 2018.

Authors: Christiane Ahlheim, Sebastian Bobadilla-Suarez, Kurt Braunlich,
Giles Greenway, & Olivia Guest.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import numpy as np
from scipy.stats import pearsonr


def make_components(data):
    """Factorize an array of mean beta values over all sessions.

    Arguments
    ---------
        data: n * m * o Numpy array of beta values for n voxels and m
        conditions over o sessions.

    Returns
    -------
        U: n * m Numpy array for n voxels and m conditions.
        S: m * m diagonal Numpy array.
        V: m * m Numpy array such that M = USV.T where M is the mean of the
            beta values over all sessions.

    """
    u, diag, v = np.linalg.svd(np.mean(data, axis=2), full_matrices=False)
    return (u, np.diag(diag), v.T)


def reconstruct(U, S, V, ncomp, testdata):
    """Pearson correlation between low-dimensional reconstruction of a matrix.

    Reconstruction of matrix is done based on its factors and a test set.

    Arguments
    ---------
        U: n * m Numpy array for n voxels and m conditions.
        S: m * m diagonal Numpy array.
        V: m * m Numpy array such that M = USV.T is a reconstrution of the
            original matrix.
        ncomp: Dimensionality of the reconstruction.
        testdata: n * m Numpy array for n voxels and m conditions to be
            correlated with the reconstruction.

    Returns
    -------
        Pearson correlation between the low dimensional reconstruction USV.T
        and testdata.

    """
    s_red = np.copy(S)
    # Set higher-dimensional components to zero.

    s_red[:, ncomp + 1:] = 0.0
    reconstruction = np.matmul(np.matmul(U, s_red), V.T)
    correlation, _ = pearsonr(reconstruction.ravel(), testdata.ravel())
    return correlation


def svd_nested_crossval(data, subject_ID, option='full'):
    """Estimate dimensionality for voxels for conditions and sessions.

    Arguments
    ---------
        data: n * m * o Numpy array of beta values for n voxels and m
            conditions over o sessions.
        option: 'full' or 'mean'; default: 'full'.

    Returns
    -------
        subject_ID: Unique indentifier for each subject.
        test_run: Which test set was used.
        winning_model: Winning models/dimensionality.
        test_correlation: The out-of-samplel correlation for the winning model.

    """
    n_beta, n_session = data.shape[1:]
    n_comp = n_beta - 1
    rmat = np.zeros((n_comp, n_session - 1, n_session))
    test_run = []

    if option == 'full':
        winning_model = np.zeros((n_session - 1, n_session), dtype='int32')
        test_correlation = np.zeros((n_session - 1, n_session))
    elif option == 'mean':
        winning_model = np.zeros(n_session, dtype='int32')
        test_correlation = np.zeros(n_session)
    else:
        raise ValueError('Unknown option: "' + str(option) +
                         '"; "full" and "mean" are the only options.')

    for i_test in range(n_session):
        # Remove the data for the ith session to produce test and validation
        # sets.
        data_val = np.delete(data, i_test, axis=2)
        data_test = data[:, :, i_test]

        for j_val in range(n_session - 1):
            # Remove the data for the jth session to produce training and test
            # sets.
            data_val_train = np.delete(data_val, j_val, axis=2)

            # Facorize the mean of the training set over all sessions.
            Uval, Sval, Vval = make_components(data_val_train)

            # Find the correlations between reconstructions of the training set
            # for each possible dimensionality and the test set.
            for comp in range(n_comp):
                rmat[comp, j_val, i_test] = reconstruct(Uval, Sval, Vval, comp,
                                                        data_val[:, :, j_val])

            if option == 'full':
                test_run.append(i_test + 1)

                rmax = rmat[:, j_val, i_test]

                # The index with the greatest correlation corresponds to the
                # best dimensionality, so the incremented index must be
                # returned.
                winning_model[j_val, i_test] = np.argmax(rmax)

                U, S, V = make_components(data_val)

                test_correlation[j_val, i_test] = \
                    reconstruct(
                        U, S, V, winning_model[j_val, i_test], data_test)
            elif option != 'mean':
                raise ValueError('Unknown option: "' + str(option) +
                                 '"; "full" and "mean" are the only options.')

        if option == 'mean':
            test_run.append(i_test + 1)

            # Mean Fisher z-transformation:
            meanr = np.mean(np.arctanh(rmat[:, :, i_test]), axis=1)
            # The index with the greatest correlation corresponds to the best
            # dimensionality, so the incremented index must be returned.
            winning_model[i_test] = np.argmax(meanr)

            U, S, V = make_components(data_val)

            test_correlation[i_test] = \
                reconstruct(U, S, V, winning_model[i_test], data_test)
        elif option != 'full':
            raise ValueError('Unknown option: "' + str(option) +
                             '"; "full" and "mean" are the only options.')

    return (subject_ID, test_run, winning_model + 1, test_correlation)
