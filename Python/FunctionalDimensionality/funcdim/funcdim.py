
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
%along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import itertools
from multiprocessing import Pool

import numpy as np
import scipy

from funcdim.crossval import svd_nested_crossval
from funcdim.searchlight import searchlight_sphere, searchlight_map 
from funcdim.tfce import tfce_onesample

def covdiag(x,df=None):
    """Based on the function from the RSA Toolbox:
    https://github.com/rsagroup/rsatoolbox/blob/develop/%2Brsa/%2Bstat/covdiag.m
    arguments:
        x: Numpy array of size t * n, t observations of n random variables.
        df: Degrees of freedom, defaults to t-1.
    returns:
        Invertible covariance matrix estimator as an n * n Numpy array,
        accroding to the optimal shrikage method as outline in Ledoit& Wolf (2005). 
    """

    t, n = x.shape

    if not df:
        df = t - 1
    
    # De-mean returns.
    x = x - x.mean(axis=0)
    
    # Compute the sample covariance matrix.
    sample = np.matmul(x.T,x) / df
    # Compute prior
    prior = np.diag(np.diag(sample))
    
    # Compute shrinkage parameter using Ledoit-Wolf method. 
    d = np.linalg.norm(sample - prior,ord='fro')**2 / n
    y = x**2
    
    r2 = (np.matmul(y.T,y).sum()/df**2 - (sample**2).sum()/df) / n
    
    shrinkage = np.max([0,np.min([1.0,r2/d])])
    
    # Regularize the estimate.
    return shrinkage * prior + (1.0 - shrinkage) * sample

def pre_proc(data, res):
    n_voxels, n_betas, n_sessions = data.shape
    beta_norm = np.zeros(data.shape)
    for i_session in range(n_sessions):
        cov_e = covdiag(res[:,:,i_session].T)
        beta_norm[:,:,i_session] = np.matmul(data[:,:,i_session].T,
            scipy.linalg.sqrtm(scipy.linalg.inv(cov_e))).T
        
    return beta_norm - beta_norm.mean(axis=1).reshape(n_voxels, 1, n_sessions)

def run_searchlight(voxel_key, data, res, voxel_map, n_sessions):
    """
    arguments:
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
        if res == None:
            data_searchlight = data[indices,:,:]
        else:
            data_searchlight = pre_proc(data[indices,:,:], res[indices,:,:])

        return svd_nested_crossval(data_searchlight)
    # ...otherwise returns NaNs.
    else:
        return tuple(3*[np.full(n_sessions, np.nan)])
       
def searchlight_estimator(data, res, voxel_keys, voxel_map, n_voxels, n_sessions):
    """
    arguments:
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
    
    args = ((voxel,) + (data, res, voxel_map, n_sessions) for voxel in voxel_keys)
    for vox, estimates in enumerate(itertools.starmap(run_searchlight, args)):
        best, outer, alter = estimates
        bestn[vox,:] = best
        r_outer[vox,:] = outer
        r_alter[vox,:] = alter
        
    return {'bestn':bestn, 'r_outer':r_outer, 'r_alter':r_alter}
    
def roi_estimator(data,res,n_sessions):
    if res == None:
        bestn, r_outer, r_alter = svd_nested_crossval(data)
    else:
        bestn, r_outer, r_alter = svd_nested_crossval(pre_proc(data, res))

    return {'bestn':bestn, 'r_outer':r_outer, 'r_alter':r_alter}
    
def functional_dimensionality(wholebrain_all, n_subjects, mask, sphere=None,
    res=None, test=tfce_onesample):
    """
    arguments:
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
    iter_brain, first_brain = itertools.tee(wholebrain_all,2)

    unmasked_voxels, n_conditions, n_sessions = first_brain.__next__().shape

    flat_mask = mask.ravel()
    
    # Iterate over sets of voxels that are active in the mask.  
    masked_brains = (brain[flat_mask] for brain in iter_brain)
    
    if res == None:
        residuals = (None for i in range(n_subjects))
    else:
        residuals = (r[flat_mask] for r in res)
        
    if sphere:
        # Searchlight:
        estimator = searchlight_estimator
        """Build a dictionary of spherical neighbourhoods around each
        active voxel in the mask."""
        voxel_map = searchlight_map(mask, sphere, min_voxels = n_conditions)
        """The dictionary's keys are the index arrays of active voxels
        in the mask converted to bytes."""
        voxel_keys = [voxel.tobytes() for voxel in np.argwhere(mask)]
        n_voxels = len(voxel_keys)
        all_output_shape = (n_subjects, n_voxels, n_sessions)
        mean_shape = (n_voxels, n_subjects)
        args = (brain + (voxel_keys, voxel_map, n_voxels, n_sessions)
            for brain in zip(masked_brains, residuals))
    else:
        # ROI:
        estimator = roi_estimator
        all_output_shape = (n_subjects, n_sessions)
        mean_shape = (1,n_subjects)
        args = (brain + (n_sessions,) for brain in zip(masked_brains, residuals))
    
    estimator_pool = Pool()
    
    estimates = estimator_pool.starmap(estimator, args)

    bestn_all = np.zeros(all_output_shape)
    r_outer_all = np.zeros(all_output_shape)
    r_alter_all = np.zeros(all_output_shape)
    
    for subject, estimate in enumerate(estimates):
        bestn_all[subject] = estimate['bestn']
        r_outer_all[subject] = estimate['r_outer']
        r_alter_all[subject] = estimate['r_alter']
        
    mean_bestn = np.zeros(mean_shape)
    mean_r_outer = np.zeros(mean_shape)
    mean_r_alter = np.zeros(mean_shape)
    std_bestn = np.zeros(mean_shape)
    
    mean_axis = len(all_output_shape) - 2
    
    for subject in range(n_subjects):
        mean_bestn[:,subject] = bestn_all[subject].mean(axis=mean_axis)
        mean_r_outer[:,subject] = r_outer_all[subject].mean(axis=mean_axis)
        mean_r_alter[:,subject] = r_alter_all[subject].mean(axis=mean_axis)
        std_bestn[:,subject] = bestn_all[subject].std(axis=mean_axis)
    
    results = {'bestn': mean_bestn, 'std_bestn':std_bestn,
        'r_outer':mean_r_outer, 'r_alter':mean_r_alter}
            
    #  Determining statistical significance, defaults to TFCE.
    if sphere and test:
        vol_test = np.empty(shape = mask.shape + (n_subjects,))
        vol_test[:] = np.nan
        vol_test[mask,:] = mean_r_outer
        results['test'] = test(vol_test)

    return results

