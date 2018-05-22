"""Copyright 2018, Giles Greenway
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

"""Based on MatlabTFCE by Mark Allen Thornton:
https://github.com/markallenthornton/MatlabTFCE
"""

import itertools
from multiprocessing import Pool

import numpy as np
from scipy import ndimage

struct = np.ones((3,3,3), dtype='int')

def tfce_transform(img, H, E, dh):
    """Perform the TFCE transform.
    arguments:
        img: 3D image as a Numpy array.
        H: Height exponent.
        E: Extent exponent.
        dh: Threshold step-size.
    
    """
    threshs = np.arange(0, np.nanmax(img), dh)[1:]
    tfced = np.zeros(img.shape)
    
    for threshold in threshs:
        # Find connected components.
        comp, _ = ndimage.label((img > threshold).astype('int'), structure=struct)
        # Find the size of each connected component in voxels.
        vox_per_cc = list(zip(*np.unique(comp, return_counts=True)))
        cluster_size = np.zeros(img.shape, dtype='int')
        # Build an image where each voxel contains the size of its connected component.
        for label, size in vox_per_cc[1:]:
            cluster_size[comp == label] = size
        # Add the contribution from each threshold.
        tfced += (cluster_size**E) * (threshold**H)
        
    return tfced * dh

def onesample_perm(imgs,implicitmask,tvals,subjects,root_subjects,bsize,H,E,dh):
    roccimgs = np.copy(imgs)
    np.random.seed()
    # Permuate flipping signs at random.
    for subject in [subject for subject in np.arange(subjects) if np.random.choice([True,False])]:
        roccimgs[:,subject] = -imgs[:,subject]
    
    # Calculate the permutation statistic.
    rstats = np.mean(roccimgs, axis=1) / (np.std(roccimgs, axis=1) / root_subjects)
        
    rbrain = np.zeros(bsize)
    rbrain[implicitmask] = rstats
    rbrain = tfce_transform(rbrain,H,E,dh)
    rstats = rbrain[implicitmask]    

    # Compare the maxima to the true statistic.
    return (np.max(rstats, axis=0) >= tvals).astype('int')

def tfce_onesample(imgs, nperm=5000, H=2, E=0.5, dh=0.1):
    """
    arguments:
        imgs: Numpy array of shape x * y * z * n_images
    keyword-arguments:
        nperm: Number of permutations, defaults to 5000.
        H: Height exponent, defaults to 2.
        E: Extent exponent, defaults to 0.5.
        dh: Threshold step-size, default to 0.1.
     returns:   
        Numpy array of shape x * y * z * n_images containing corrected p-values.        
    
    """
    subjects = imgs.shape[-1]
    bsize = imgs.shape[:-1]
    
    root_subjects = np.sqrt(subjects)
    
    # Calculate the true mean image.
    truestat = np.nanmean(imgs, axis=3) / (np.nanstd(imgs, axis=3) / root_subjects)
    implicitmask = ~np.isnan(truestat)
    tfcestat = tfce_transform(truestat,H,E,dh)
    
    tvals = tfcestat[implicitmask]
    nvox = tvals.size
    
    # Extract occupied voxels for permutation tests.
    occimgs = np.zeros((nvox, subjects))
    for subject in range(subjects):
        occimgs[:,subject] = imgs[:,:,:,subject][implicitmask]
        
    exceedances = np.zeros(nvox, dtype='int')
    
    # Cycle through the permutations.
    tfce_pool = Pool()
    permdata = itertools.repeat((occimgs,implicitmask,tvals,subjects,root_subjects,bsize,H,E,dh), nperm)
    perms = tfce_pool.starmap(onesample_perm, permdata)
    for p in perms:
        exceedances += p 

    # Create the corrected p-value image.
    pcorr = np.ones(bsize)
    pcorr[implicitmask] = exceedances / nperm 

    return pcorr
