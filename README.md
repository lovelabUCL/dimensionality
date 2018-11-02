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
    - [Demo](#demo)
  - [Python](#python)
    - [Requirements](#requirements-1)
    - [Installation](#installation)
    - [Usage](#usage-1)
    - [Demo](#demo-1)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Functional Dimensionality

[![Build Status](https://travis-ci.org/lovelabUCL/dimensionality.svg?branch=master)](https://travis-ci.org/lovelabUCL/dimensionality) [![codecov](https://codecov.io/gh/lovelabUCL/dimensionality/branch/master/graph/badge.svg)](https://codecov.io/gh/lovelabUCL/dimensionality) [![GitHub license](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)](https://github.com/lovelabUCL/dimensionality/blob/master/LICENSE)



## Authors

-   **Christiane Ahlheim**: wrote original codebase in Matlab.

-   **Giles Greenway**: wrote original codebase in Python and optimised Matlab code.

-   **Sebastian Bobadilla-Suarez, Kurt Braunlich, & Olivia Guest**: modified Python and Matlab codebases for new features and release.

## Overview

This is a method implemented in both Matlab and Python to estimate the functional dimensionality of (neural) data, as described in
**Estimating the functional dimensionality of neural representations**
Ahlheim, C. & [Love, B.C.](http://bradlove.org) (2018). [Estimating the functional dimensionality of neural representations](https://www.sciencedirect.com/science/article/pii/S1053811918305226). Neuroimage, DOI: [10.1016/j.neuroimage.2018.06.015](https://doi.org/10.1016/j.neuroimage.2018.06.015).

Guidance for the Matlab and Python implementations is provided below.

For those interested in an overview of how the method works, a brief description follows. The method tests all possible dimensionalities where each dimensionality corresponds to a model. The best performing model is selected and is evaluated on held out test data. The procedure uses nested training, validation, and test sets to evaluate models. Each model is trained on the training data, then evaluated on the validation data. The model that performs best on the validation data is then retrained on both the training and validation data and is then tested on the held out test data. This held out test provides an unbiased evaluation of the winning model's performance in terms of the Pearson correlation between the model's prediction for the test set and the actual test set data. According to the null hypothesis, this correlation should be zero.

There are many such evaluations performed by the code. Each run plays the role of training, validation, and test set for all possible combinations. Therefore, a design with 6 runs will have 6 possible test runs X 5 possible arrangements of validation and training runs, which will result in 30 distinct outputs from our function. Each output consists of the subject number, which run was used as the the test set, winning model dimensionality, and the test correlation. When the optional flag is set to "mean", the method does some aggregation for the user, following the method reported in [Ahlheim and Love (2018)](https://www.sciencedirect.com/science/article/pii/S1053811918305226), and there is only one output for each run. Whether this flag is used or not, the outputs can be used to determine statistical significance or to estimate the functional dimensionality (please see [Ahlheim and Love, 2018](https://www.sciencedirect.com/science/article/pii/S1053811918305226)).

## Citation

Please cite this paper if you use this software (also see [CITATION.cff](https://github.com/lovelabUCL/dimensionality/blob/master/CITATION.cff) and [CITATION.bib](https://github.com/lovelabUCL/dimensionality/blob/master/CITATION.bib) for a BibTeX file):

-   **Estimating the functional dimensionality of neural representations**
    Ahlheim, C. & [Love, B.C.](http://bradlove.org) (2018). [Estimating the functional dimensionality of neural representations](https://www.sciencedirect.com/science/article/pii/S1053811918305226). Neuroimage, DOI: [10.1016/j.neuroimage.2018.06.015](https://doi.org/10.1016/j.neuroimage.2018.06.015).

## MATLAB

### Requirements

-   [SPM12](http://www.fil.ion.ucl.ac.uk/spm/software/spm12/).
-   [The RSA-toolbox](https://www.mrc-cbu.cam.ac.uk/methods-and-resources/toolboxes/).
-   [Matlab Stan](http://mc-stan.org/users/interfaces/matlab-stan) (only needed to run the hierarchical model).
-   Model comparison could be done using [PSIS](https://github.com/avehtari/PSIS).
-   The `covdiag` function from [https://github.com/jooh/pilab](https://github.com/jooh/pilab) (shrinkage of the residual covariance matrix during pre-whitening).

### Usage

`functional_dimensionality(wholebrain_all, mask, subject_IDs, full)`

This function returns the following variables:
-   `winning_models`: best dimensionality
-   `test_correlations`: correlation for winning model for out-of-sample test run
-   `test_runs`: indices for the test run
-   `subject_IDs`: subject identifier


### Demo

A small (&lt;1Mb) amount of simulated data with nominal dimensionality 4 for 64 voxels and 6 sessions for 20 subjects is provided in the `./Matlab/demo_data` directory, along with a 4x4x4 mask with all voxels set to "true". This can be used as follows:

```matlab
clear all; close all; clc;

matfile = load('demo_data/sample_data.mat');
[vox, cond, sessions, subjects] = size(matfile.sample_data);
wholebrain_all = {};
subject_IDs=[];
for i = 1:subjects                   
    brain = matfile.sample_data(:,:,:,i);
    wholebrain_all{i} = brain;
    subject_IDs = [subject_IDs i];
end

% select 'full' or 'mean' option:
%   - full=0: estimate best dimensionality by averaging over inner CV loop. (as
%     in paper)
%   - full=1: return separate estimates for each inner CV loop.
full = 1;

% separate estimates for each run:
[subject_IDs, test_runs, winning_models, test_correlations]=functional_dimensionality(wholebrain_all, ...
    'demo_data/sample_mask.img',subject_IDs,full);

% average over runs:
median_winning_model = median(winning_models);
median_test_correlation = median(test_correlations);

% point estimate of best dimensionality:
fprintf('winning model overall = %.2f\n',median(median_winning_model(:)))

% write results to CSV file:
csvwrite('demo_output.csv', [subject_IDs, test_runs, winning_models, test_correlations])
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

```
python --version
Python 3.x.x
```

If not, use `python3` where we use `python` in all examples herein. If you don't have that command, please [install Python 3](https://www.python.org/downloads/).

### Usage

Within the Python interpreter:

```python
from funcdim.funcdim import functional_dimensionality
```

The function takes the arguments: `wholebrain_all`, `n_subjects`, `mask`, `subject_IDs=None`, `res=None`, `option='full'`.
The `wholebrain_all` data is passed in as an iterator of Numpy arrays of dimensions `n_voxels` x `n_conditions` x `n_runs` over `n_subjects`, which may be a Numpy array of dimensions `n_subjects` x `n_voxels` x `n_conditions` x `n_runs`. For pre-whitening, residuals may be passed in a similar format using the keyword argument `res`. A mask should be passed in as a boolean Numpy array, which can be produced using [Nibabel](http://nipy.org/nibabel/). The keyword argument `option` accepts either 'full' (return separate estimates for each inner cross-validation loop) or 'mean' (estimate best dimensionality by averaging over inner cross-validation loop). The results are returned in a dictionary with keys:

-   `winning_model`: best dimensionality
-   `test_correlation`: correlation for winning model for out-of-sample test run
-   `test_run`: indices for the test run
-   `subject_ID`: subject identifier

```python
functional_dimensionality(wholebrain_all, n_subjects, mask, subject_IDs=None, res=None, option='full')
```

### Demo

A small (<1Mb) ammount of simulated data with nominal dimensionality 4 is provided in the "Python/demo_data" directory. This can be used as follows (or run the `demo_real_data.py` in `Python/FunctionalDimensionality/demos/`):
:

```python
from funcdim.funcdim import functional_dimensionality
import numpy as np
import pandas as pd

# load the sample data.
data = np.load('./demos/demo_data/sample_data.npy')
# "data" has the shape (64, 16, 6, 20), containing beta values for 64 voxels,
# 16 conditions, 6 sessions, 20 subjects.
nsubs = 20

# Create the subject IDs.
subject_IDs = [str(i) for i in range(1, nsubs + 1)]

# Create a 4*4*4 mask (all True) for the 64 voxels.
mask = np.ones((4, 4, 4), dtype='bool')

# Create an iterator over the 20 subjects.
all_subjects = (data[:, :, :, i] for i in range(nsubs))

# Find the dimensionality.
results = functional_dimensionality(all_subjects, nsubs, mask,
                                    subject_IDs=subject_IDs)

# Put the output results into a dataframe and save as a CSV file.
df = pd.DataFrame.from_dict(results)
df.to_csv('./demos/demo_data/demo_real_data_output.csv')

# Show the median dimensionality:
print(df['winning_model'].median())
```

The result of running that last line:

```python
>>> df['winning_model'].median()
4.0
```
