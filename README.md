<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Functional Dimensionality](#functional-dimensionality)
  - [Authors](#authors)
  - [Overview](#overview)
  - [Citation](#citation)
  - [MATLAB](#matlab)
    - [Requirements](#requirements)
    - [Usage](#usage)
      - [ROI](#roi)
      - [Searchlight](#searchlight)
    - [Demo](#demo)
  - [Python](#python)
    - [Requirements](#requirements-1)
    - [Installation](#installation)
    - [Usage](#usage-1)
      - [ROI](#roi-1)
      - [Searchlight](#searchlight-1)
    - [Demo](#demo-1)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Functional Dimensionality

[![Build Status](https://travis-ci.org/lovelabUCL/dimensionality.svg?branch=master)](https://travis-ci.org/lovelabUCL/dimensionality)

## Authors

-   **Christiane Ahlheim**: wrote original codebase in Matlab.

-   **Giles Greenway**: wrote original codebase in Python and optimised Matlab code.

-   **Sebastian Bobadilla-Suarez, Kurt Braunlich, & Olivia Guest**: modified Python and Matlab codebases for new features and release.

## Overview

This is a method implemented in both Matlab and Python to estimate the functional dimensionality of (neural) data, as described in
**Estimating the functional dimensionality of neural representations**
Ahlheim, C. & [Love, B.C.](http://bradlove.org) (2017). [Estimating the functional dimensionality of neural representations](https://www.sciencedirect.com/science/article/pii/S1053811918305226). Neuroimage, DOI: [10.1016/j.neuroimage.2018.06.015](https://doi.org/10.1016/j.neuroimage.2018.06.015).

Guidance for the Matlab and Python implementations is provided below.

## Citation

Please cite this paper if you use this software (also see [CITATION.cff](https://github.com/lovelabUCL/dimensionality/blob/master/CITATION.cff) and [CITATION.bib](https://github.com/lovelabUCL/dimensionality/blob/master/CITATION.bib) for a BibTeX file):

-   **Estimating the functional dimensionality of neural representations**
    Ahlheim, C. & [Love, B.C.](http://bradlove.org) (2017). [Estimating the functional dimensionality of neural representations](https://www.sciencedirect.com/science/article/pii/S1053811918305226). Neuroimage, DOI: [10.1016/j.neuroimage.2018.06.015](https://doi.org/10.1016/j.neuroimage.2018.06.015).

## MATLAB

Estimate the functional dimensionality in a ROI or a searchlight in MATLAB.

### Requirements

-   [SPM12](http://www.fil.ion.ucl.ac.uk/spm/software/spm12/).
-   [The RSA-toolbox](https://www.mrc-cbu.cam.ac.uk/methods-and-resources/toolboxes/).
-   [Matlab Stan](http://mc-stan.org/users/interfaces/matlab-stan) (only needed to run the hierarchical model).
-   Model comparison could be done using [PSIS](https://github.com/avehtari/PSIS).
-   The `covdiag` function from [https://github.com/jooh/pilab](pilab) (shrinkage of the residual covariance matrix during pre-whitening).
-   TFCE correction can be run using FSL or with [MatlabTFCE](https://github.com/markallenthornton/MatlabTFCE).

### Usage

#### ROI

`functional_dimensionality(wholebrain_all, mask)`

#### Searchlight

`functional_dimensionality(wholebrain_all, mask, 'sphere',<sphere_radius>)`

`wholebrain_all`: Load your 1st level beta estimates as a cell of size `n_subject`, each with a matrix of size `n_voxel` x `n_conditions` x `n_runs`.

`mask`: Path to mask.

Currently, pre-whitening is implemented by passing in the full path to "SPM.mat", as "spmfile" eg:

`functional_dimensionality(wholebrain_all, '/path/to/mask', 'spmfile','/path/to/SPM.mat')`

### Demo

A small (&lt;1Mb) amount of simulated data with nominal dimensionality 4 for 64 voxels and 6 sessions for 20 subjects is provided in the "Matlab/demo_data" directory, along with a 4x4x4 mask with all voxels set to "true". This can be used as follows:

```matlab
matfile = load('demo_data/sample_data.mat');
[vox, cond, sessions, subjects] = size(matfile.sample_data);
wholebrain_all = {};
for i = 1:subjects                   
    brain = matfile.sample_data(:,:,:,i);
    wholebrain_all{i} = brain;
end

% full=1: return separate estimates for each inner CV loop. 
% full=0: estimate best dimensionality by averaging over inner CV loop.
full=1; 

% separate estimates for each run
[bestn_all,r_outer_all,r_alter_all,test_tfce]=functional_dimensionality(wholebrain_all, ...
    'demo_data/sample_mask.img',full);

% average over runs:
for i_subject = 1:subjects
    mean_r_outer(:, i_subject) = mean(r_outer_all{i_subject},1);
    mean_r_alter(:, i_subject) = mean(r_alter_all{i_subject},1);
    mean_bestn(:, i_subject)   = mean(bestn_all{i_subject},1);
end

% point estimate of best dimensionality:
fprintf('bestn = %.2f\n',mean(mean_bestn(:)))

% full (full=0) = 4.54
% mean (full=1) = 5.01
```      


## Python

### Requirements

-   Python 3
-   [Nibabel](http://nipy.org/nibabel/)
-   [Numpy](http://www.numpy.org/)
-   [Scipy](https://www.scipy.org/)

More info in [requirements.txt](https://github.com/lovelabUCL/dimensionality/blob/master/Python/FunctionalDimensionality/requirements.txt).

### Installation

If you want to install this to use as a library please follow the instructions below, if you want to modify this code to use as a basis for your own method please [clone](https://help.github.com/articles/cloning-a-repository/) this repository instead.

From within the `FunctionalDimensionality` directory, and preferably within a [Virtualenv](https://virtualenv.pypa.io/en/stable/), install as follows:

```python
python setup.py build sdist
pip install .
```

Please use Python 3, i.e., make sure your `python` command is calling python 3:

```python
python --version
Python 3.x.x
```

If not, use `python3` where we use `python` in all examples herein. If you don't have that command, please [install Python 3](https://www.python.org/downloads/).

### Usage

Within the Python interpreter:

```python
from funcdim.funcdim import functional_dimensionality
```

The function takes the arguments: wholebrain_all, n_subjects, mask, sphere=None, res=None, test.
The `wholebrain_all` data is passed in as an iterator of Numpy arrays of dimensions `n_voxels` x `n_conditions` x `n_runs` over `n_subjects`, which may be a Numpy array of dimensions `n_subjects` x `n_voxels` x `n_conditions` x `n_runs`. For pre-whitening, residuals may be passed in a similar format using the keyword argument `res`. A mask should be passed in as a boolean Numpy array, which can be produced using [Nibabel](http://nipy.org/nibabel/). The results are returned in a dictionary with keys:

-   bestn, mean best dimensionality
-   r_outer, mean lowest correlation
-   r_alter, mean highest correlation

#### ROI

`functional_dimensionality(wholebrain_all, n_subjects, mask, res=None)`

Each item in the dictionary will be an array with a single value for each subject, averaged over each session.

#### Searchlight

`functional_dimensionality(wholebrain_all, n_subjects, mask, sphere=<sphere_radius>, test=tfce_onesample, res=None)`
For searchlights, if a sphere radius is specified, the results are corrected by applying threshold free cluster enhancement ([TFCE](https://www.ncbi.nlm.nih.gov/pubmed/18501637)) by default using a limited implementation based on the [Matlab version](https://github.com/markallenthornton/MatlabTFCE) by Mark Allen Thornton. To bypass this, users may set the `test` keyword argument to `None`, or pass in a function of their own. This should accept a Numpy array of dimensions `x_voxels` x `y_voxels` x `z_voxels` x `n_images` and return a single image as a Numpy array.

Each item in the dictionary will be an array of voxel arrays, averaged over each session.

### Demo

A small (&lt;1Mb) ammount of simulated data with nominal dimensionality 4 is provided in the "Python/demo_data" directory. This can be used as follows (or run the `demo.py` in `Python/FunctionalDimensionality`):
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

print(results['bestn'].mean())
```

The result of running that last line:

```python
>>> results['bestn'].mean()
4.541666666666667
```
