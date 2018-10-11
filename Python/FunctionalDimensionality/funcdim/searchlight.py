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
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import numpy as np


def searchlight_sphere(vox, radius):
    """Find the set of voxel coordinates within a sphere relative to centre.

    Arguments
    ---------
        vox: Voxel size.
        radius: Sphere radius.

    Returns
    -------
        n * 3 Numpy array of coordinates of n voxels relative to the centre
        of the sphere.

    """
    # Minimum radius in voxels:
    min_margin_vox = np.floor(radius / vox).astype('int')
    grid = np.meshgrid(*3 * [np.arange(-min_margin_vox, min_margin_vox + 1)])
    # True where voxels are within the sphere:
    sphere = sum([(vox * g)**2 for g in grid]) < radius**2
    # n * 3 array of indices of voxels within the sphere:
    sphere_subs = np.flip(np.array(np.nonzero(sphere)).T, axis=1)
    # Return voxel indices relative to the centre of the sphere:
    return sphere_subs - np.rint(np.array(sphere.shape) / 2).astype('int')


def searchlight_map(mask, sphere, min_voxels=0, vox=3):
    """Find indices of voxels in a sphere centered around each voxel in a mask.

    Find the indices of active voxels within a sphere centered around each
    active voxel in a mask, relative to a flattened array of active voxels in
    the mask.

    Arguments
    ---------
        mask: Mask as a 3D Numpy array of booleans.
        sphere: Sphere radius in mm, assuming 3mm voxels.
        min_voxels: Sets of voxels must be larger than this to be included.
        vox: Voxel size in mm.

    Returns
    -------
        Dictionary whose keys are the hashed coordinates of each active voxel
        within the mask using the "to_bytes" method of each Numpy array of
        coordinates. The values are lists of indices of active voxels within
        the sphere, if they are larger than min_voxels.

    """
    sphere_indices = searchlight_sphere(vox, sphere)
    voxel_map = {}

    # Iterate over all active voxels within the mask:
    for voxel in np.argwhere(mask):
        # Centre the sphere around the voxel:
        neighbourhood = sphere_indices + voxel
        # Find voxels with negative indices, or that lie outside the mask:
        out_of_bounds = np.any((neighbourhood < np.zeros(3, dtype='int'))
                               | (neighbourhood > mask.shape), axis=1)
        # Remove "out-of-bounds" voxels:
        neighbourhood = neighbourhood[np.nonzero(~out_of_bounds)]
        # Tuples of the x, y and z voxel indices:
        neighbourhood_index = [col.flatten()
                               for col in np.hsplit(neighbourhood, 3)]
        # Indices of active voxels in the sphere, relative to a flattened array
        # of active voxels in the mask.
        flat_mask_voxels = np.array(
            np.argwhere(mask[neighbourhood_index]).flat)
        # Only add the voxels if they are sufficient.
        if flat_mask_voxels.size > min_voxels:
            voxel_map[voxel.tobytes()] = flat_mask_voxels

    return voxel_map
