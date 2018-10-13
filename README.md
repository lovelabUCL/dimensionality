<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Functional Dimensionality](#functional-dimensionality)
  - [Overview](#overview)
  - [Citation](#citation)
  - [MATLAB](#matlab)
    - [Requirements](#requirements)
    - [Usage](#usage)
      - [ROI](#roi)
      - [Searchlight](#searchlight)
    - [Demonstration](#demonstration)
  - [Python](#python)
    - [Requirements](#requirements-1)
    - [Installation](#installation)
    - [Usage](#usage-1)
      - [ROI](#roi-1)
      - [Searchlight](#searchlight-1)
    - [Demonstration](#demonstration-1)
  - [General pipeline](#general-pipeline)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Functional Dimensionality

[![Build Status](https://travis-ci.org/lovelabUCL/dimensionality.svg?branch=master)](https://travis-ci.org/lovelabUCL/dimensionality)

## Overview
This is a method implemented in both Matlab and Python to estimate the functional dimensionality of (neural) data, as described in
**Estimating the functional dimensionality of neural representations**
Ahlheim, C. & [Love, B.C.](http://bradlove.org) (2017). [Estimating the functional dimensionality of neural representations](https://www.sciencedirect.com/science/article/pii/S1053811918305226). Neuroimage, DOI: [10.1016/j.neuroimage.2018.06.015](https://doi.org/10.1016/j.neuroimage.2018.06.015).

Guidance for the Matlab and Python implementations is provided below.

## Citation
Please cite this paper if you use this software (also see [CITATION.cff](https://github.com/lovelabUCL/dimensionality/blob/master/CITATION.cff) and [CITATION.bib](https://github.com/lovelabUCL/dimensionality/blob/master/CITATION.bib) for a BibTeX file):

- **Estimating the functional dimensionality of neural representations**
Ahlheim, C. & [Love, B.C.](http://bradlove.org) (2017). [Estimating the functional dimensionality of neural representations](https://www.sciencedirect.com/science/article/pii/S1053811918305226). Neuroimage, DOI: [10.1016/j.neuroimage.2018.06.015](https://doi.org/10.1016/j.neuroimage.2018.06.015).

## MATLAB

Estimate the functional dimensionality in a ROI or a searchlight in MATLAB.

### Requirements

- [SPM12](http://www.fil.ion.ucl.ac.uk/spm/software/spm12/).
- [The RSA-toolbox](https://www.mrc-cbu.cam.ac.uk/methods-and-resources/toolboxes/).
- [Matlab Stan](http://mc-stan.org/users/interfaces/matlab-stan) (only needed to run the hierarchical model).
- Model comparison could be done using [PSIS](https://github.com/avehtari/PSIS).
- The ```covdiag``` function from [https://github.com/jooh/pilab](pilab) (shrinkage of the residual covariance matrix during pre-whitening).
- TFCE correction can be run using FSL or with [MatlabTFCE](https://github.com/markallenthornton/MatlabTFCE).

### Usage    

#### ROI
```functional_dimensionality(wholebrain_all, mask)```

#### Searchlight
```functional_dimensionality(wholebrain_all, mask, 'sphere',<sphere_radius>)```

```wholebrain_all```: Load your 1st level beta estimates as a cell of size ```n_subject```, each with a matrix of size ```n_voxel``` x ```n_conditions``` x ```n_runs```.

```mask```: Path to mask.

Currently, pre-whitening is implemented by passing in the full path to "SPM.mat", as "spmfile" eg:

```functional_dimensionality(wholebrain_all, '/path/to/mask', 'spmfile','/path/to/SPM.mat')```

### Demonstration

A small (<1Mb) amount of simulated data with nominal dimensionality 4 for 64 voxels and 6 sessions for 20 subjects is provided in the "Matlab/demo_data" directory, along with a 4x4x4 mask with all voxels set to "true". This can be used as follows:

```
matfile = load('demo_data/sample_data.mat');
[vox, cond, sessions, subjects] = size(matfile.sample_data);
wholebrain_all = {};
for i = 1:subjects                   
    brain = matfile.sample_data(:,:,:,i);
    wholebrain_all{i} = brain;
end
[mean_bestn,mean_r_outer_mean_r_alter,]=functional_dimensionality(wholebrain_all,'demo_data/sample_mask.img');

```

The results should be:

```
>> mean_bestn

mean_bestn =

  Columns 1 through 5

    4.1667    4.5000    4.3333    4.6667    4.0000

  Columns 6 through 10

    4.1667    6.0000    4.0000    4.0000    3.5000

  Columns 11 through 15
transmedialint_tml_models

    5.8333    4.5000    4.0000    7.0000    5.6667

  Columns 16 through 20

    4.0000    5.0000    4.0000    4.1667    3.3333
```        

## Python

### Requirements

- Python 3
- [Nibabel](http://nipy.org/nibabel/)
- [Numpy](http://www.numpy.org/)
- [Scipy](https://www.scipy.org/)

More info in [requirements.txt](https://github.com/lovelabUCL/dimensionality/blob/master/Python/FunctionalDimensionality/requirements.txt).

### Installation

If you want to install this to use as a library please follow the instructions below, if you want to modify this code to use as a basis for your own method please [clone](https://help.github.com/articles/cloning-a-repository/) this repository instead.

From within the ```FunctionalDimensionality``` directory, and preferably within a [Virtualenv](https://virtualenv.pypa.io/en/stable/), install as follows:
```python
python setup.py build sdist
pip install .
```

Please use Python 3, i.e., make sure your ```python``` command is calling python 3:
```python
python --version
Python 3.x.x
```
If not, use ```python3``` where we use ```python``` in all examples herein. If you don't have that command, please [install Python 3](https://www.python.org/downloads/).

### Usage

Within the Python interpreter:

```python
from funcdim.funcdim import functional_dimensionality
```

The function takes the arguments: wholebrain_all, n_subjects, mask, sphere=None, res=None, test.
The ```wholebrain_all``` data is passed in as an iterator of Numpy arrays of dimensions ```n_voxels``` x ```n_conditions``` x ```n_runs``` over ```n_subjects```, which may be a Numpy array of dimensions ```n_subjects``` x ```n_voxels``` x ```n_conditions``` x ```n_runs```. For pre-whitening, residuals may be passed in a similar format using the keyword argument ```res```. A mask should be passed in as a boolean Numpy array, which can be produced using [Nibabel](http://nipy.org/nibabel/). The results are returned in a dictionary with keys:

- bestn, mean best dimensionality
- r_outer, mean lowest correlation
- r_alter, mean highest correlation

#### ROI
```functional_dimensionality(wholebrain_all, n_subjects, mask, res=None)```

Each item in the dictionary will be an array with a single value for each subject, averaged over each session.

#### Searchlight
```functional_dimensionality(wholebrain_all, n_subjects, mask, sphere=<sphere_radius>, test=tfce_onesample, res=None)```
For searchlights, if a sphere radius is specified, the results are corrected by applying threshold free cluster enhancement ([TFCE](https://www.ncbi.nlm.nih.gov/pubmed/18501637)) by default using a limited implementation based on the [Matlab version](https://github.com/markallenthornton/MatlabTFCE) by Mark Allen Thornton. To bypass this, users may set the ```test``` keyword argument to ```None```, or pass in a function of their own. This should accept a Numpy array of dimensions ```x_voxels``` x ```y_voxels``` x ```z_voxels``` x ```n_images``` and return a single image as a Numpy array.

Each item in the dictionary will be an array of voxel arrays, averaged over each session.

### Demonstration

A small (<1Mb) ammount of simulated data with nominal dimensionality 4 is provided in the "Python/demo_data" directory. This can be used as follows (or run the ```demo.py``` in ```Python/FunctionalDimensionality```):
:


```python
from funcdim.funcdim import functional_dimensionality
import numpy as np

# load the sample data.
data = np.load('demo_data/sample_data.npy')
# "data" has the shape (64, 16, 6, 20), containing beta values for 64 voxels,
# 16 conditions, 6 sessions, 20 subjects.

# Create a 4*4*4 mask (all True) for the 64 voxels.
mask = np.ones((4, 4, 4), dtype='bool')

# Create an iterator over the 20 subjects.
all_subjects = (data[:, :, :, i] for i in range(20))

# Find the dimensionality.
results = functional_dimensionality(all_subjects, 20, mask)

print(results)
```

The results should be (recall ```bestn``` is the mean best dimensionality):

```python
>>> results['bestn']
 array([[4.16666667, 4.5       , 4.33333333, 4.66666667, 4.        ,
        4.16666667, 6.        , 4.        , 4.        , 3.5       ,
        5.83333333, 4.5       , 4.        , 7.        , 5.66666667,
        4.        , 5.        , 4.        , 4.16666667, 3.33333333]])
>>> results['bestn'].mean()
4.541666666666667

```

## General pipeline
The user should:
- Load data (beta estimates for each subject: voxel x conditions x sessions).
- If pre-whitening: load residuals as well.
- Mask both residuals and data using a wholebrain or ROI mask.

The function will then, for each searchlight/ROI:

+ whiten and mean-center data within the searchlight;
+ run the nested cross-validation;
+ average training data, get all possible low-dimensional reconstructions of the training data;
+ correlate each low-dimensional reconstruction of the training data with the validation data;
+ across all partitions into training and validation, identify which dimensionality "k" resulted in the highest average correlation between the reconstructed data and the validation data;
+ average training and validation data, build k-dimensional reconstruction of the data and correlate with test-set;
+ as each run serves as a test set once, the method returns one dimensionality estimate and correlation coefficient per run.

The function returns:

- mean_bestn, mean best dimensionality
- mean_r_outer, mean lowest correlation
- mean_r_alter, mean highest correlation    
