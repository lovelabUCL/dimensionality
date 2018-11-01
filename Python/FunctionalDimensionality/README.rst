Functional Dimensionality
=========================

Authors
-------

-  **Christiane Ahlheim**: wrote original codebase in Matlab.

-  **Giles Greenway**: wrote original codebase in Python and optimised
   Matlab code.

-  **Sebastian Bobadilla-Suarez, Kurt Braunlich, & Olivia Guest**:
   modified Python and Matlab codebases for new features and release.

Overview
--------

This is a method implemented in both Matlab and Python to estimate the
functional dimensionality of (neural) data, as described in **Estimating
the functional dimensionality of neural representations** Ahlheim, C. &
`Love, B.C. <http://bradlove.org>`__ (2017). `Estimating the functional
dimensionality of neural
representations <https://www.sciencedirect.com/science/article/pii/S1053811918305226>`__.
Neuroimage, DOI:
`10.1016/j.neuroimage.2018.06.015 <https://doi.org/10.1016/j.neuroimage.2018.06.015>`__.

Guidance for the Matlab and Python implementations is provided below.

Citation
--------

Please cite this paper if you use this software (also see
`CITATION.cff <https://github.com/lovelabUCL/dimensionality/blob/master/CITATION.cff>`__
and
`CITATION.bib <https://github.com/lovelabUCL/dimensionality/blob/master/CITATION.bib>`__
for a BibTeX file):

-  **Estimating the functional dimensionality of neural
   representations** Ahlheim, C. & `Love, B.C. <http://bradlove.org>`__
   (2017). `Estimating the functional dimensionality of neural
   representations <https://www.sciencedirect.com/science/article/pii/S1053811918305226>`__.
   Neuroimage, DOI:
   `10.1016/j.neuroimage.2018.06.015 <https://doi.org/10.1016/j.neuroimage.2018.06.015>`__.

Python
------

Requirements
~~~~~~~~~~~~

-  Python 3
-  `Nibabel <http://nipy.org/nibabel/>`__
-  `Numpy <http://www.numpy.org/>`__
-  `Scipy <https://www.scipy.org/>`__

More info in
`requirements.txt <https://github.com/lovelabUCL/dimensionality/blob/master/Python/FunctionalDimensionality/requirements.txt>`__.

Installation
~~~~~~~~~~~~

If you want to install this to use as a library please follow the
instructions below, if you want to modify this code to use as a basis
for your own method please
`clone <https://help.github.com/articles/cloning-a-repository/>`__ this
repository instead.

From within the ``FunctionalDimensionality`` directory, and preferably
within a `Virtualenv <https://virtualenv.pypa.io/en/stable/>`__, install
as follows:

.. code:: python

   python setup.py build sdist
   pip install .

Please use Python 3, i.e., make sure your ``python`` command is calling
python 3:

.. code:: python

   python --version
   Python 3.x.x

If not, use ``python3`` where we use ``python`` in all examples herein.
If you don’t have that command, please `install Python
3 <https://www.python.org/downloads/>`__.

Usage
~~~~~

Within the Python interpreter:

.. code:: python

   from funcdim.funcdim import functional_dimensionality

The function takes the arguments: wholebrain_all, n_subjects, mask, subject_IDs=None, res=None, option='full'.
The `wholebrain_all` data is passed in as an iterator of Numpy arrays of dimensions `n_voxels` x `n_conditions` x `n_runs` over `n_subjects`, which may be a Numpy array of dimensions `n_subjects` x `n_voxels` x `n_conditions` x `n_runs`. For pre-whitening, residuals may be passed in a similar format using the keyword argument `res`. A mask should be passed in as a boolean Numpy array, which can be produced using [Nibabel](http://nipy.org/nibabel/). The keyword argument `option` accepts either 'full' (return separate estimates for each inner CV loop) or 'mean' (estimate best dimensionality by averaging over inner CV loop). The results are returned in a dictionary with keys:

-   winning_model: best dimensionality
-   test_correlation: correlation for winning model for out-of-sample test run
-   test_run: indices for the test run
-   subject_ID: subject identifier

ROI
^^^

``functional_dimensionality(wholebrain_all, n_subjects, mask, subject_IDs=None, res=None, option='full')``

Demo
~~~~

A small (<1Mb) ammount of simulated data with nominal dimensionality 4
is provided in the “Python/demo_data” directory. This can be used as
follows (or run the ``demo.py`` in ``Python/FunctionalDimensionality``):
:

.. code:: python

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

The result of running that last line:

.. code:: python

   >>> df['winning_model'].median()
   4.0
