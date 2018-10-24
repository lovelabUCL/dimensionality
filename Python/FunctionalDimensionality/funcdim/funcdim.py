"""Copyright 2018, Giles Greenway & Christiane Ahlheim.

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
from funcdim.searchlight import searchlight_map
from funcdim.tfce import tfce_onesample
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
        beta_norm[:, :, i_session] = np.matmul(data[:, :, i_session].T,
                                               scipy.linalg.
                                               fractional_matrix_power(cov_e,
                                                                       -0.5)).T

    return beta_norm - beta_norm.mean(axis=1).reshape(n_voxels, 1, n_sessions)


def run_searchlight(voxel_key, data, res, voxel_map, n_sessions):
    """Run searchlight.

    Arguments
    ---------
        voxel_key: Voxel coordinates as a Numpy array converted to bytes.
        data: Numpy array of shape n_voxels * n_conditions * n_subjects,
            where n_voxels is the number of active voxels in the mask used.
        voxel_map: Dictionary of arrays of flattened indices of voxels in
            spherical regions for each voxel key.
        n_sessions: Number of sessions.

    """
    indices = voxel_map.get(voxel_key, [])

    # Only perform cross-validation if sufficient voxels were returned...
    if len(indices) > 0:
        if res is None:
            data_searchlight = data[indices, :, :]
        else:
            data_searchlight = pre_proc(
                data[indices, :, :], res[indices, :, :])

        return svd_nested_crossval(data_searchlight)
    # ...otherwise returns NaNs.
    else:
        return tuple(3 * [np.full(n_sessions, np.nan)])


def searchlight_estimator(data, res, voxel_keys, voxel_map, n_voxels):
    """Searchlight estimator.

    Arguments
    ---------
        data: Numpy array of shape n_voxels * n_conditions * n_subjects,
            where n_voxels is the number of active voxels in the mask used.
        voxel_keys: Indices of active voxels within the mask, as bytes.
        voxel_map: Dictionary of arrays of flattened indices of voxels in
            spherical regions for each voxel key.
        n_voxels: Number of active voxels in the mask used.
        n_sessions: Number of sessions.
    """
    n_conditions, n_sessions = data.shape[1:]

    output_shape = (n_voxels, n_sessions)

    bestn = np.zeros(output_shape)
    r_outer = np.zeros(output_shape)
    r_alter = np.zeros(output_shape)

    args = ((voxel,) + (data, res, voxel_map, n_sessions)
            for voxel in voxel_keys)
    for vox, estimates in enumerate(itertools.starmap(run_searchlight, args)):
        best, outer, alter = estimates
        bestn[vox, :] = best
        r_outer[vox, :] = outer
        r_alter[vox, :] = alter

    return {'bestn': bestn, 'r_outer': r_outer, 'r_alter': r_alter}


def roi_estimator(data, res):
    """ROI estimator."""
    if res is None:
        bestn, r_outer, r_alter, rmat = svd_nested_crossval(data)
    else:
        bestn, r_outer, r_alter, rmat = svd_nested_crossval(pre_proc(data,
                                                                     res))

    return {'bestn': bestn, 'r_outer': r_outer, 'r_alter': r_alter,
            'rmat': rmat}


def functional_dimensionality(wholebrain_all, n_subjects, mask, sphere=None,
                              res=None, test=tfce_onesample):
    """Estimate functional dimensionality.

    Arguments
    ---------
        wholebrain_all: Iterable of n_voxels * n_conditions * n_sessions Numpy
            arrays over n_subjects. This can be an
            n_subjects * n_voxels * n_conditions * n_sessions array.
        mask: Mask as an i * j * k Numpy array of booleans such that
            i * j * k = n_voxels.
        sphere: Sphere radius in mm if a searchlight is to be performed.
            (If not specified, ROI is applied.)
        test: Function that performs a statistical test on a Numpy array of
            i * j * k voxels * n_subjects, returning an i * j * k array.
            This defaults to an implementation of TFCE, based on the
            ttest_onesample function in Mark Allen Thornton's MATLAB
            implementation:
                https://github.com/markallenthornton/MatlabTFCE
            Set this to "None" or False to ignore this step.

    """
    iter_brain, first_brain = itertools.tee(wholebrain_all, 2)

    unmasked_voxels, n_conditions, _ = first_brain.__next__().shape

    flat_mask = mask.ravel()

    # Iterate over sets of voxels that are active in the mask.
    masked_brains = (brain[flat_mask] for brain in iter_brain)

    if res is None:
        residuals = (None for i in range(n_subjects))
    else:
        residuals = res

    if sphere:
        # Searchlight:
        estimator = searchlight_estimator
        # Build a dictionary of spherical neighbourhoods around each active
        # voxel in the mask.
        voxel_map = searchlight_map(mask, sphere, min_voxels=n_conditions)
        # The dictionary's keys are the index arrays of active voxels in the
        # mask converted to bytes.
        voxel_keys = [voxel.tobytes() for voxel in np.argwhere(mask)]
        n_voxels = len(voxel_keys)
        mean_axis = 1
        mean_shape = (n_voxels, n_subjects)
        args = (brain + (voxel_keys, voxel_map, n_voxels)
                for brain in zip(masked_brains, residuals))
    else:
        # ROI:
        estimator = roi_estimator
        mean_axis = 0
        mean_shape = (1, n_subjects)
        args = (brain for brain in zip(masked_brains, residuals))

    estimator_pool = Pool()

    estimates = estimator_pool.starmap(estimator, args)

    bestn_all = []
    r_outer_all = []
    r_alter_all = []
    rmat_all = []

    for estimate in estimates:
        bestn_all.append(estimate['bestn'])
        r_outer_all.append(estimate['r_outer'])
        r_alter_all.append(estimate['r_alter'])
        rmat_all.append(estimate['rmat'])

    mean_bestn = np.zeros(mean_shape)
    mean_r_outer = np.zeros(mean_shape)
    mean_r_alter = np.zeros(mean_shape)
    if not sphere:
        std_bestn = np.zeros(mean_shape)

    for subject in range(n_subjects):
        mean_bestn[:, subject] = bestn_all[subject].mean(axis=mean_axis)
        mean_r_outer[:, subject] = r_outer_all[subject].mean(axis=mean_axis)
        mean_r_alter[:, subject] = r_alter_all[subject].mean(axis=mean_axis)
        if not sphere:
            std_bestn[:, subject] = bestn_all[subject].std(axis=mean_axis)

    # results = {'bestn': mean_bestn,
            # 'r_outer': mean_r_outer, 'r_alter': mean_r_alter}

    results = {'bestn': np.asarray(bestn_all),
               'r_outer': np.asarray(r_outer_all),
               'r_alter': np.asarray(r_alter_all),
               'rmat': np.asarray(rmat_all)}

    if not sphere:
        results['std_bestn'] = std_bestn

    #  Determining statistical significance, defaults to TFCE.
    if sphere and test:
        vol_test = np.empty(shape=mask.shape + (n_subjects,))
        vol_test[:] = np.nan
        vol_test[mask, :] = mean_r_outer
        results['test'] = test(vol_test)

    return results
