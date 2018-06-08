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

from itertools import chain, tee
import os

import nibabel as nib
import numpy as np
from scipy.io import loadmat

def load_spm(spm_path):
    return loadmat('/'.join([spm_path,'SPM.mat']))['SPM']

def get_residuals(spm, mask):
    matrix = spm[0][0]['xY']['VY'][0][0]['mat']
    
    dim = spm[0][0]['xY']['VY'][0][0]['dim'][0][0][0]
    
    nscan, nbeta = spm[0][0]['xX']['X'][0][0].shape
    
    chunksize = int(np.floor((2**26/8)/nbeta))
    data_size = np.prod(dim)
    nbchunks = int(np.ceil(data_size/chunksize))

    low_index, high_index = tee(chain(range(0,data_size,chunksize),[data_size]))
    high_index.__next__()
    chunk_indices = zip(low_index,high_index)
    
    for start, end in chunk_indices:
        m = mask.ravel()[start:end]

        y = np.zeros((nscan,end-start))

def spm_beta_files(spm,path):
    vbeta = spm['Vbeta'][0][0]['fname'][0]
    return ['/'.join([path,b[0]]) for b in vbeta]

def spm_beta_images(beta_files):
    for image in map(nib.load, beta_files):
        yield image

def load_brain(spm_path):
    spm = load_spm(spm_path)
    
    sess = spm['Sess'][0][0][0]
    n_sessions = len(sess)
    n_conditions = len(sess['U'][0][0][0])
    
    beta_files = spm_beta_files(spm, spm_path)
    n_betas = len(beta_files)
    
    image = spm_beta_images(beta_files).__next__()
    image_size = np.product(image.shape)
    image_dtype = image.get_data_dtype()
    brain_shape = image.shape[:] + (n_betas,)
    new_shape = (image_size, n_betas//n_sessions, n_sessions)
    
    brain = np.zeros(brain_shape, dtype=image_dtype)
    
    for beta, image in enumerate(spm_beta_images(beta_files)):
        brain[:,:,:,beta] = image.get_data()
    return np.reshape(brain, new_shape)[:,0:n_conditions,:]

def brains_from_spm(subject_path):
    subject_dirs = sorted(os.listdir(subject_path))
    subject_spmpaths=['/'.join([subject_path,d]) for d in subject_dirs]
    
    n_subjects = len(subject_dirs)
    
    return n_subjects, map(load_brain, subject_spmpaths)

def load_mask(mask_file):
    return nib.load(mask_file).get_data() > 0
    

