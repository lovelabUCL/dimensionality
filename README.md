#  Estimating the functional dimensionality of neural representations
Ahlheim, C. & [Love, B.C.](http://bradlove.org) (2017). [Estimating the functional dimensionality of neural representations](https://www.sciencedirect.com/science/article/pii/S1053811918305226). Neuroimage, DOI: [10.1016/j.neuroimage.2018.06.015](https://doi.org/10.1016/j.neuroimage.2018.06.015)

(Data is available at the [Open Science Framework](https://osf.io/tpq92/).)

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
    
#### ROI: ```functional_dimensionality(wholebrain_all, mask)```

#### Searchlight: ```functional_dimensionality(wholebrain_all, mask, 'sphere',<sphere_radius>)```

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

```
python setup.py build sdist```
pip install .
```

Within the Python interpreter:

```from funcdim.funcdim import functional_dimensionality```

The ```wholebrain_all``` data is passed in as an iterator of Numpy arrays of dimensions ```n_voxels``` x ```n_conditions``` x ```n_runs``` over ```n_subjects```, which may be a Numpy array of dimensions ```n_subjects``` x ```n_voxels``` x ```n_conditions``` x ```n_runs```. For pre-whitening, residuals may be passed in a similar format using the keyword argument ```res```. A mask should be passed in as a boolean Numpy array, which can be produced using [Nibabel](http://nipy.org/nibabel/).

#### Roi: ```functional_dimensionality(wholebrain_all, n_subjects, mask, res=None)``` 

#### Searchlight: ```functional_dimensionality(wholebrain_all, n_subjects, mask, sphere=<sphere_radius>, test=tfce_onesample, res=None)```
For searchlights, if a sphere radius is specified, the results are corrected by applying threshold free cluster enhancement ([TFCE](https://www.ncbi.nlm.nih.gov/pubmed/18501637)) by default using a limited implementation based on the [Matlab version](https://github.com/markallenthornton/MatlabTFCE) by Mark Allen Thornton. To bypass this, users may set the ```test``` keyword argument to ```None```, or pass in a function of their own. This should accept a Numpy array of dimensions ```x_voxels``` x ```y_voxels``` x ```z_voxels``` x ```n_images``` and return a single image as a Numpy array.

# Demonstration

A small (<6Mb) sub-set of the simulated data available at the [OSF](https://osf.io/tpq92/)) has
been included in the ```demo_data``` directory. The file ```sim_data_sample.mat``` contains \beta values for
64 voxels over 16 conditions and 6 sessions for 10 repetitions, 2 subjects and 2 noise levels with nominal dimensionalities of 6, 8 and 12. The data is stored in the ```sample_sim_data``` array. (The full version has 100 repetitions, 20 subjects and 10 noise levels.) Scripts to demonstrate the ```svd_nested_crossval``` function are provided in Matlab and Python.

## Matlab

```
>> dimensionality_demo '/data/sim_data_sample.mat'   
dimension: 1
         noise-level: 1
                 mean best dimensionality: 5.666667
                 mean best correlation: 0.182385
                 mean highest correlation: 0.159273
         noise-level: 2
                 mean best dimensionality: 7.233333
                 mean best correlation: 0.105642
                 mean highest correlation: 0.100822
dimension: 2
         noise-level: 1
                 mean best dimensionality: 9.566667
                 mean best correlation: 0.133728
                 mean highest correlation: 0.136079
         noise-level: 2
                 mean best dimensionality: 10.666667
                 mean best correlation: 0.104528
                 mean highest correlation: 0.109759
dimension: 3
         noise-level: 1
                 mean best dimensionality: 12.566667
                 mean best correlation: 0.126082
                 mean highest correlation: 0.130933
         noise-level: 2
                 mean best dimensionality: 12.775000
                 mean best correlation: 0.116159
                 mean highest correlation: 0.121186
```

## Python

```
dimensionality_demo.py /data/sim_data_sample.mat
64 voxels, 16 stimuli, 6 sessions, 10 sims,
    2 subjects, 3 dims, 2 noise-levels

dimension: 0
        noise-level: 0,
                mean best dimensionality: 5.67,
                mean best correlation: 0.18,
                mean highest correlation: 0.16
        noise-level: 1,
                mean best dimensionality: 7.23,
                mean best correlation: 0.11,
                mean highest correlation: 0.10
dimension: 1
        noise-level: 0,
                mean best dimensionality: 9.57,
                mean best correlation: 0.13,
                mean highest correlation: 0.14
        noise-level: 1,
                mean best dimensionality: 10.67,
                mean best correlation: 0.10,
                mean highest correlation: 0.11
dimension: 2
        noise-level: 0,
                mean best dimensionality: 12.57,
                mean best correlation: 0.13,
                mean highest correlation: 0.13
        noise-level: 1,
                mean best dimensionality: 12.78,
                mean best correlation: 0.12,
                mean highest correlation: 0.12
```
