#  Estimating the functional dimensionality of neural representations
Ahlheim, C. & [Love, B.C.](http://bradlove.org) (2017). [Estimating the functional dimensionality of neural representations](https://www.biorxiv.org/content/early/2018/03/29/232454). bioRxiv, DOI: [10.1101/232454](https://doi.org/10.1101/232454)

# MATLAB implementation

This set of functions allows you to estimate the functional dimensionality in a ROI or a searchlight.

## Requirements:

- [SPM12](http://www.fil.ion.ucl.ac.uk/spm/software/spm12/).
- [The RSA-toolbox](https://www.mrc-cbu.cam.ac.uk/methods-and-resources/toolboxes/).
- [Matlab Stan](http://mc-stan.org/users/interfaces/matlab-stan) (only needed to run the hierarchical model).
- Model comparison could be done using [PSIS](https://github.com/avehtari/PSIS).
- The ```covdiag``` function from [https://github.com/jooh/pilab](pilab) (shrinkage of the residual covariance matrix during pre-whitening).
- TFCE correction can be run using FSL or with [MatlabTFCE](https://github.com/markallenthornton/MatlabTFCE).

## Usage:    
    
### ROI: ```functional_dimensionality(wholebrain_all, mask)```

### Searchlight: ```functional_dimensionality(wholebrain_all, mask, 'sphere',<sphere_radius>)```

```wholebrain_all```: Load your 1st level beta estimates as a cell of size ```n_subject```, each with a matrix of size ```n_voxel``` x ```n_conditions``` x ```n_runs```.

```mask```: Path to mask.
    
Currently, pre-whitening is implemented by passing in the full path to "SPM.mat", as "spmfile" eg:

```functional_dimensionality(wholebrain_all, '/path/to/mask', 'spmfile','/path/to/SPM.mat')```

### General pipeline:
- Load data (beta estimates for each subject: voxel x conditions x sessions).
- If pre-whitening: load residuals as well.
- Mask both residuals and data using a wholebrain or ROI mask.
- For each searchlight/ROI:
  + whiten and mean-center data within the searchlight;
  + run the nested cross-validation;
  + average training data, get all possible low-dimensional reconstructions of the training data;
  + correlate each low-dimensional reconstruction of the training data with the validation data;
  + across all partitions into training and validation, identify which dimensionality "k" resulted in the highest average correlation between the reconstructed data and the validation data;
  + average training and validation data, build k-dimensional reconstruction of the data and correlate with test-set;
  + as each run serves as a test set once, the method returns one dimensionality estimate and correlation coefficient per run.
  
# Python implementation

## Requirements:

- [Nibabel](http://nipy.org/nibabel/)
- [Numpy](http://www.numpy.org/)
- [Scipy](https://www.scipy.org/)

## Usage:

From within the ```FunctionalDimensionality``` directory, and preferably within a [Virtualenv](https://virtualenv.pypa.io/en/stable/), install as follows:
```python setup.py build sdist```
```pip install .```

From the Python interpreter:

```from funcdim.funcdim import functional_dimensionality```

The ```wholebrain_all``` data is passed in as an iterator of Numpy arrays of dimensions ```n_voxels``` x ```n_conditions``` x ```n_runs``` over ```n_subjects```, which may be a Numpy array of dimensions ```n_subjects``` x ```n_voxels``` x ```n_conditions``` x ```n_runs```. For pre-whitening, residuals may be passed in a similar format using the keyword argument ```res```. A mask should be passed in as a boolean Numpy array, which can be produced using [Nibabel](http://nipy.org/nibabel/).

### Roi: ```functional_dimensionality(wholebrain_all, n_subjects, mask, res=None)``` 

### Searchlight: ```functional_dimensionality(wholebrain_all, n_subjects, mask, sphere=<sphere_radius>, test=tfce_onesample, res=None)```
For searchlights, if a sphere radius is specified, the results are corrected by applying threshold free cluster enhancement ([TFCE](https://www.ncbi.nlm.nih.gov/pubmed/18501637)) by default using a limited implementation based on the [Matlab version](https://github.com/markallenthornton/MatlabTFCE) by Mark Allen Thornton. To bypass this, users may set the ```test``` keyword argument to ```None```, or pass in a function of their own. This should accept a Numpy array of dimensions ```x_voxels``` x ```y_voxels``` x ```z_voxels``` x ```n_images``` and return a single image as a Numpy array.