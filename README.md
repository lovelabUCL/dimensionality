This is a tool implemented in both Matlab and Python for estimating the dimensionality of neural data, as described in 
**Estimating the functional dimensionality of neural representations**
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

## Installation:

From within the ```FunctionalDimensionality``` directory, and preferably within a [Virtualenv](https://virtualenv.pypa.io/en/stable/), install as follows:

```python
python setup.py build sdist
pip install .
```

## Usage:

Within the Python interpreter:

```python
from funcdim.funcdim import functional_dimensionality
```

The ```wholebrain_all``` data is passed in as an iterator of Numpy arrays of dimensions ```n_voxels``` x ```n_conditions``` x ```n_runs``` over ```n_subjects```, which may be a Numpy array of dimensions ```n_subjects``` x ```n_voxels``` x ```n_conditions``` x ```n_runs```. For pre-whitening, residuals may be passed in a similar format using the keyword argument ```res```. A mask should be passed in as a boolean Numpy array, which can be produced using [Nibabel](http://nipy.org/nibabel/).

#### Roi: ```functional_dimensionality(wholebrain_all, n_subjects, mask, res=None)``` 

#### Searchlight: ```functional_dimensionality(wholebrain_all, n_subjects, mask, sphere=<sphere_radius>, test=tfce_onesample, res=None)```
For searchlights, if a sphere radius is specified, the results are corrected by applying threshold free cluster enhancement ([TFCE](https://www.ncbi.nlm.nih.gov/pubmed/18501637)) by default using a limited implementation based on the [Matlab version](https://github.com/markallenthornton/MatlabTFCE) by Mark Allen Thornton. To bypass this, users may set the ```test``` keyword argument to ```None```, or pass in a function of their own. This should accept a Numpy array of dimensions ```x_voxels``` x ```y_voxels``` x ```z_voxels``` x ```n_images``` and return a single image as a Numpy array.

# Demonstration

A small (<6Mb) sub-set of the simulated data available at the [OSF](https://osf.io/tpq92/)) has
been included in the ```demo_data``` directory. The file ```sim_data_sample.mat``` contains &beta; values for
simulations with ground-truth dimensionalities of 4, 8, and 12 over 2 noise levels . The data is stored in the ```sample_sim_data``` array. (The full version is 2.5Gb, with 100 repetitions, 20 subjects and 10 noise levels.) Scripts to demonstrate the ```svd_nested_crossval``` function are provided in Matlab and Python. They return the mean best estimates of the dimensionalities for each noise level over all subjects and sessions. The mean correlations between data for each session and the highest and lowest dimensional reconstructions of all other sessions are also given.

Here are the results for applying the method to the full simulated dataset as described in the [paper](https://www.sciencedirect.com/science/article/pii/S1053811918305226):
(The full 100 repetitions over 20 subjects and 10 noise levels are used.)

"A: Distributions of single-subject posterior dimensionality estimates for a ground-truth dimensionality of 4, 8, or 12 and increasing noise levels. As noise increases, the 
estimates become less accurate and less certain, as indicated by the width of the distributions. For the highest noise level, the posterior distributions for all 
ground-truth dimensionalities overlap largely.
 
B: Average reconstruction correlations for the different ground-truth dimensionalities and increasing noise levels. As the noise level increases, reconstruction 
correlations drop, and this effect is the same across the three different ground-truth dimensionalities."

![fig 5 from the paper](https://raw.githubusercontent.com/lovelabUCL/dimensionality/staging/img/full_simulation_results.jpg)

The following output from the demonstration scripts corresponds to the first two noise levels in the figure, for each ground-truth
dimensionality of 4, 8 and 12.

## Matlab

```
>> dimensionality_demo 'demo_data/sim_data_sample.mat'
ground-truth dimensionality: 4
         noise-level: 1
                 mean best dimensionality: 4.162500
                 mean lowest correlation: 0.271799
                 mean highest correlation: 0.228741
         noise-level: 2
                 mean best dimensionality: 4.779167
                 mean lowest correlation: 0.201328
                 mean highest correlation: 0.170237
ground-truth dimensionality: 8
         noise-level: 1
                 mean best dimensionality: 8.795833
                 mean lowest correlation: 0.241126
                 mean highest correlation: 0.230273
         noise-level: 2
                 mean best dimensionality: 9.483333
                 mean lowest correlation: 0.174794
                 mean highest correlation: 0.170913
ground-truth dimensionality: 12
         noise-level: 1
                 mean best dimensionality: 12.375000
                 mean lowest correlation: 0.182957
                 mean highest correlation: 0.185597
         noise-level: 2
                 mean best dimensionality: 11.795833
                 mean lowest correlation: 0.123619
                 mean highest correlation: 0.129265
```

## Python

```
dimensionality_demo.py demo_data/sim_data_sample.mat

ground-truth dimensionality: 4
        noise-level: 0,
                mean best dimensionality: 4.16,
                mean lowest correlation: 0.27,
                mean highest correlation: 0.23
        noise-level: 1,
                mean best dimensionality: 4.78,
                mean lowest correlation: 0.20,
                mean highest correlation: 0.17

ground-truth dimensionality: 8
        noise-level: 0,
                mean best dimensionality: 8.80,
                mean lowest correlation: 0.24,
                mean highest correlation: 0.23
        noise-level: 1,
                mean best dimensionality: 9.48,
                mean lowest correlation: 0.17,
                mean highest correlation: 0.17

ground-truth dimensionality: 12
        noise-level: 0,
                mean best dimensionality: 12.38,
                mean lowest correlation: 0.18,
                mean highest correlation: 0.19
        noise-level: 1,
                mean best dimensionality: 11.80,
                mean lowest correlation: 0.12,
                mean highest correlation: 0.13
```
