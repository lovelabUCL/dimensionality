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

import nibabel as nib
import numpy as np
import os
from scipy.io import loadmat


def load_spm(spm_path):
    """Load SPM file."""
    return loadmat('/'.join([spm_path, 'SPM.mat']))['SPM']


def spm_beta_files(spm, path):
    """SPM beta files."""
    vbeta = spm['Vbeta'][0][0]['fname'][0]
    return ['/'.join([path, b[0]]) for b in vbeta]


def spm_beta_images(beta_files):
    """SPM beta images."""
    for image in map(nib.load, beta_files):
        yield image


def load_brain(spm_path):
    """Load brain."""
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
    new_shape = (image_size, n_betas // n_sessions, n_sessions)

    brain = np.zeros(brain_shape, dtype=image_dtype)

    for beta, image in enumerate(spm_beta_images(beta_files)):
        brain[:, :, :, beta] = image.get_data()
    return np.reshape(brain, new_shape)[:, 0:n_conditions, :]


def brains_from_spm(subject_path):
    """Brains from SPM."""
    subject_dirs = sorted(os.listdir(subject_path))
    subject_spmpaths = ['/'.join([subject_path, d]) for d in subject_dirs]

    n_subjects = len(subject_dirs)

    return n_subjects, map(load_brain, subject_spmpaths)


def load_mask(mask_file):
    """Load mask."""
    return nib.load(mask_file).get_data() > 0


def demo_data(functional_dims=4, nvoxels=64, nconditions=16, nruns=6,
              nsubs=20):
    """Generate demo data with a set dimensionality for tests and demo."""
    # Check nvoxels is a cube:
    cube_check = int(np.round(nvoxels**(1 / 3)))
    if cube_check**3 != nvoxels:
        raise ValueError('"nvoxels" must a cube: ' + str(nvoxels) +
                         ' is not a cube')

    # "data" has the shape (nvoxels, nconditions, nruns, nsubs), containing
    # "beta" values for nvoxels
    data = np.random.multivariate_normal(
        np.zeros((nconditions,)), np.eye(nconditions), size=(nvoxels))
    data[:, functional_dims:] = np.ones((data[:, functional_dims:].shape))
    data = data.reshape((nvoxels, nconditions, 1))
    data = np.tile(data, (nruns))
    data = data.reshape((nvoxels, nconditions, nruns, 1))
    data = np.tile(data, (nsubs))
    return data
