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

from funcdim.crossval import svd_nested_crossval
import itertools
from multiprocessing import Pool
import numpy as np
import scipy


def covdiag(x, df=None):
    """Based on the function from the RSA Toolbox.

    See:
    https://github.com/rsagroup/rsatoolbox/blob/develop/%2Brsa/%2Bstat/covdiag.m

    Arguments
    ---------
        x: Numpy array of size t * n, t observations of n random variables.
        df: Degrees of freedom, defaults to t-1.

    Returns
    -------
        Invertible covariance matrix estimator as an n * n Numpy array,
        accroding to the optimal shrikage method as outline in Ledoit& Wolf
        (2005).

    """
    t, n = x.shape

    if df is None:
        df = t - 1

    # De-mean returns.
    x = x - x.mean(axis=0)

    # Compute the sample covariance matrix.
    sample = np.matmul(x.T, x) / df
    # Compute prior
    prior = np.diag(np.diag(sample))

    # Compute shrinkage parameter using Ledoit-Wolf method.
    d = 1.0 / n * np.linalg.norm(sample - prior, ord='fro')**2
    y = x**2

    r2 = 1.0 / (n * df**2) * np.matmul(y.T, y).sum() - \
        1.0 / (n * df) * (sample**2).sum()

    r2_by_d = r2 / d
    if np.isnan(r2_by_d):
        r2_by_d = 1.0

    shrinkage = np.max([0, np.min([1.0, r2_by_d])])

    # Regularize the estimate.
    return shrinkage * prior + (1.0 - shrinkage) * sample


def pre_proc(data, res):
    """Pre-process data."""
    n_voxels, n_betas, n_sessions = data.shape
    beta_norm = np.zeros(data.shape)
    for i_session in range(n_sessions):
        cov_e = covdiag(res[:, :, i_session].T)
        beta_norm[:, :, i_session] = \
            np.matmul(data[:, :, i_session].T, scipy.linalg.
                      fractional_matrix_power(cov_e, -0.5)).T

    return beta_norm - beta_norm.mean(axis=1).reshape(n_voxels, 1, n_sessions)


def roi_estimator(data, res, subject_IDs, option='full'):
    """ROI estimator."""
    if res is None:
        subject_ID, test_run, winning_model, test_correlation = \
            svd_nested_crossval(data, subject_IDs, option)
    else:
        subject_ID, test_run, winning_model, test_correlation = \
            svd_nested_crossval(pre_proc(data, res), subject_IDs, option)

    return {'subject_ID': np.tile(subject_ID, len(test_run)),
            'test_run': test_run, 'winning_model': winning_model,
            'test_correlation': test_correlation}


def functional_dimensionality(wholebrain_all, n_subjects, mask, res=None,
                              option='full', subject_IDs=None):
    """Estimate functional dimensionality.

    Arguments
    ---------
        wholebrain_all: Iterable of n_voxels * n_conditions * n_sessions Numpy
            arrays over n_subjects. This can be an
            n_subjects * n_voxels * n_conditions * n_sessions array.
        mask: Mask as an i * j * k Numpy array of booleans such that
            i * j * k = n_voxels.
        option: 'full' or 'mean'; default: 'full'.
        subject_IDs: unique identifiers for each subject; default
                     range(1, n_subjects + 1)

    """
    if subject_IDs is None:
        subject_IDs = [str(i) for i in range(1, n_subjects + 1)]
    else:
        assert len(subject_IDs) == n_subjects

    option = [option for n in range(n_subjects)]

    iter_brain, first_brain = itertools.tee(wholebrain_all, 2)

    unmasked_voxels, n_conditions, _ = first_brain.__next__().shape

    flat_mask = mask.ravel()

    # Iterate over sets of voxels that are active in the mask.
    masked_brains = (brain[flat_mask] for brain in iter_brain)

    if res is None:
        residuals = (None for i in range(n_subjects))
    else:
        residuals = res

    args = (brain for brain in zip(
        masked_brains, residuals, subject_IDs, option))
    estimator_pool = Pool()
    estimates = estimator_pool.starmap(roi_estimator, args)

    subject_ID = []
    test_run = []
    winning_model = []
    test_correlation = []

    for estimate in estimates:
        subject_ID.append(estimate['subject_ID'])
        test_run.append(estimate['test_run'])
        winning_model.append(estimate['winning_model'])
        test_correlation.append(estimate['test_correlation'])

    results = {'subject_ID': np.asarray(subject_ID).flatten(),
               'test_run': np.asarray(test_run).flatten(),
               'winning_model': np.asarray(winning_model).flatten(),
               'test_correlation': np.asarray(test_correlation).flatten()
               }

    return results
