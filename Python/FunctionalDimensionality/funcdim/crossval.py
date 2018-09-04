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

import numpy as np
from scipy.stats import pearsonr

def make_components(data):
    """Factorize an array of mean beta values over all sessions.
    product(U, s_red, V.T) 

    arguments:
        data: n * m * o Numpy array of beta values for n voxels and m
        conditions over o sessions.
        
    returns:
        U: n * m Numpy array for n voxels and m conditions.
        S: m * m diagonal Numpy array.
        V: m * m Numpy array such that M = USV.T where M is the mean of the
            beta values over all sessions. 
    """
    u, diag, v = np.linalg.svd(np.mean(data, axis=2),full_matrices=False)
    return (u, np.diag(diag), v.T)
    
def reconstruct(U,S,V,ncomp,testdata):
    """Find the Pearson correlation between a low-dimensional reconstruction
    of a matrix from its factors and a test set.
    
    arguments:
        U: n * m Numpy array for n voxels and m conditions.
        S: m * m diagonal Numpy array.
        V: m * m Numpy array such that M = USV.T is a reconstrution of the
            original matrix.
        ncomp: Dimensionality of the reconstruction.
        testdata: n * m Numpy array for n voxels and m conditions to be
            correlated with the reconstruction.
            
    returns:
        Pearson correlation between the low dimensional reconstruction USV.T
        and testdata.
    """
    s_red = np.copy(S)
    # Set higher-dimensional components to zero.
    s_red[:,ncomp+1:] = 0.0
    reconstruction = np.matmul(np.matmul(U, s_red), V.T) 
    correlation, _ = pearsonr(reconstruction.ravel(), testdata.ravel())
    return correlation
    
def svd_nested_crossval(data):
    """Estimate the degree of dimensionality for a set of voxels for given
    sets of conditions and sessions.
    
    arguments:
        data: n * m * o Numpy array of beta values for n voxels and m
            conditions over o sessions.
            
    returns:
        bestn: Array of best estimates of dimensionality for each session.
        r_outer: Correlations between data for each session and the
            best low-dimensional reconstruction of all other sessions.
        r_alter: Correlations between data for each session and the
            highest dimensional reconstruction of all other sessions.
    
    """
    n_beta,n_session = data.shape[1:]
    n_comp = n_beta - 1;
    rmat = np.zeros((n_comp, n_session-1, n_session))
    bestn = np.zeros(n_session, dtype='int32')
    r_outer = np.zeros(n_session)
    r_alter = np.zeros(n_session)
        
    for i_test in range(n_session):
        """Remove the data for the ith session to produce test and validation
        sets."""
        data_val = np.delete(data,i_test,axis=2)
        data_test = data[:,:,i_test]
        
        for j_val in range(n_session-1):
            """Remove the data for the jth session to produce training and
            test sets."""
            data_val_train = np.delete(data_val,j_val,axis=2)
            
            #Facorize the mean of the training set over all sessions.
            Uval, Sval, Vval = make_components(data_val_train)
            
            """Find the correlations between reconstructions of the training
            set for each possible dimensionality and the test set."""
            for comp in range(n_comp):
                rmat[comp,j_val,i_test] = reconstruct(Uval,Sval,Vval,comp,
                    data_val[:,:,j_val])
        
        # Mean Fisher z-transformation:
        meanr = np.mean(np.arctanh(rmat[:,:,i_test]),axis=1)
        """The index with the greatest correlation corresponds to the best
        dimensionality, so the incremented index must be returned."""
        bestn[i_test] = np.argmax(meanr)
        
        U, S, V = make_components(data_val)
        
        r_outer[i_test] = reconstruct(U,S,V,bestn[i_test],data_test)
        r_alter[i_test] = reconstruct(U,S,V,n_comp-1,data_test);
        
    return (1 + bestn, r_outer, r_alter)
