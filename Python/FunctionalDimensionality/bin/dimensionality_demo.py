#!/usr/bin/env python3
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

import sys

import numpy as np
from scipy.io import loadmat

from funcdim.crossval import svd_nested_crossval


def data_mesh(data):
    """Return an iterable of indices over all simulations, subjects,
    dimensions and noise-levels in the given Numpy array."""
    beta_mesh = np.meshgrid(*map(np.arange,data.shape[3:]))
    yield from list(zip(*map(np.ravel,beta_mesh)))
    
    
def run_crossval(data):
    """Runs svd_nested_crossval on the given Numpy array.
    Displays the mean best dimensionality and mean correlations of the best
    and highest dimensionalities with data from all other sessions, for each
    nominal dimensionality and noise level."""
    try:
        assert len(data.shape) == 7
    except:
        print("""Expected an array of dimensions:
            voxels * stimuli * sessions * sims * subjects * dims * noise-levels""")
        return

    print("""{} voxels, {} stimuli, {} sessions, {} sims,
    {} subjects, {} dims, {} noise-levels""".format(*data.shape))
    print()

    result_shape = (data.shape[2],) + data.shape[3:]
    
    all_bestn = np.zeros(result_shape)
    all_router = np.zeros(result_shape)
    all_ralter = np.zeros(result_shape)
    
    for beta in data_mesh(data):
        rep, subject, dim, noise = beta
        bestn, r_outer, r_alter = svd_nested_crossval(
            data[:,:,:,rep,subject,dim,noise])
        all_bestn[:,rep,subject,dim,noise] = bestn
        all_router[:,rep,subject,dim,noise] = r_outer
        all_ralter[:,rep,subject,dim,noise] = r_alter
        
    for dim in range(data.shape[5]):
        print("dimension: {}".format(dim))
        for noise in range(data.shape[6]):
            print(
                """\tnoise-level: {:d},
                mean best dimensionality: {:03.2f},
                mean best correlation: {:03.2f},
                mean highest correlation: {:03.2f}""".format(noise,
                all_bestn[:,:,:,dim,noise].mean(),
                all_router[:,:,:,dim,noise].mean(),
                all_ralter[:,:,:,dim,noise].mean()))



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""No file specified.
              Usage: dimensionality_demo.py datafile [matlab-var]
              where "datafile" is in .npy or .mat format.
              "matlab-var" specifies the Matlab variable to use, default is "sample_sim_data".
              Expects an array of dimensions:
                    voxels * stimuli * sessions * sims * subjects * dims * noise-levels""")
        path = None
    else:
        path = sys.argv[1]

    ext = None
        
    if path != None:
        try:
            ext = path.split('.')[-1]
            assert ext in ['mat','npy']
        except:
            print("{} is not in .mat. or .npy format.".format(path))
    
    data = np.array([False])
    
    if ext == 'mat':
        if len(sys.argv) >= 3:
            mat_var = sys.argv[2]
        else:
            mat_var = 'sample_sim_data'
            
        try:
            matrix = loadmat(path)
        except:
            print("Could not open {}.".format(path))
            matrix = None
            
            
        if matrix != None:
            try:
                data = matrix[mat_var]
            except:
                print("{} does not contain the variable {}.".format(path,mat_var))
                print(list(matrix.keys()))
                
    if ext == 'npy':
        try:
            data = np.load(path)
        except:
            print("Could not open {}.".format(path))
    
    if data.any():
        run_crossval(data)

        
