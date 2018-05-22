
==================================================================
Estimating the functional dimensionality of neural representations
==================================================================

Ahlheim, C. & `Love, B.C.
<http://bradlove.org>`_ (2017). `Estimating the functional dimensionality of neural representations
<https://www.biorxiv.org/content/early/2018/03/29/232454>`_. bioRxiv, DOI: `10.1101/232454
<https://doi.org/10.1101/232454>`_.

This set of functions allows you to estimate the functional dimensionality in a ROI or a searchlight.

General pipeline:
=================
- Load data (beta estimates for each subject: voxels x conditions x sessions).
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
  
Requirements:
=============

- Nibabel_
- Numpy_
- Scipy_

.. _Nibabel: http://nipy.org/nibabel/
.. _Numpy: http://www.numpy.org/
.. _Scipy: https://www.scipy.org/ 

Usage:
======

Within the Python interpreter:

``from funcdim.funcdim import functional_dimensionality``

Roi: ``functional_dimensionality(wholebrain_all, n_subjects, mask, res=None)`` 

Searchlight: ``functional_dimensionality(wholebrain_all, n_subjects, mask, sphere=<sphere_radius>, test=tfce_onesample, res=None)``

The ``wholebrain_all`` data is passed in as an iterator of Numpy arrays of dimensions ``n_voxels`` * ``n_conditions`` * ``n_runs`` over ``n_subjects``, which may be a Numpy array of dimensions ``n_subjects`` * ``n_voxels`` * ``n_conditions`` * ``n_runs``. For pre-whitening, residuals may be passed in a similar format using the keyword argument ``res``. A mask should be passed in as a boolean Numpy array, which can be produced using Nibabel_.

For searchlights, if a sphere radius is specified, the results are corrected by applying threshold free cluster enhancement (TFCE_) default using a limited implementation based on the Matlab version_https://github.com/markallenthornton/MatlabTFCE by Mark Allen Thornton. To bypass this users may set the ``test`` keyword argument to ``None``, or pass in a function of their own. This should accept a Numpy array of dimensions ``x_voxels`` * ``y_voxels`` * ``z_voxels`` * ``n_images`` and return a single image as a Numpy array.

.. _TFCE: https://www.ncbi.nlm.nih.gov/pubmed/18501637/

Users interested only in the core of the method can import the ``svd_nested_crossval`` function from ``funcdim.crossval``. This accepts a Numpy array of dimensions ``n_voxels`` * ``n_conditions`` * ``n_runs``.  


