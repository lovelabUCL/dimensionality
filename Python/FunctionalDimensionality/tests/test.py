"""Testing."""

from funcdim.funcdim import functional_dimensionality
import numpy as np
from output import dictionary as correct
import unittest


class TestState(unittest.TestCase):  # noqa:D101

    def test_demo(self):  # noqa:D102
        # load the sample data.
        data = np.load('demo_data/sample_data.npy')
        # "data" has the shape (64, 16, 6, 20)

        # Create a 4*4*4 mask (all True) for the 64 voxels.
        mask = np.ones((4, 4, 4), dtype='bool')

        # Create an iterator over the 20 subjects.
        all_subjects = (data[:, :, :, i] for i in range(20))

        # Find the dimensionality.
        results = functional_dimensionality(all_subjects, 20, mask)

        # Check the keys are identical.
        self.assertEqual(sorted(results.keys()),
                         sorted(correct.keys()))

        # Loop through to compare the contents of both dictionaries:
        for (key, value) in results.items():
            self.assertTrue(np.allclose(value, correct[key]))


if __name__ == '__main__':
    unittest.main()
