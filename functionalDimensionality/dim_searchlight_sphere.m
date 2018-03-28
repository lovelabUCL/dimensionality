function ctrRelSphereSUBs = dim_searchlight_sphere(vox,rad)
%% “Copyright 2018, Christiane Ahlheim”
%% This program is free software: you can redistribute it and/or modify
%% it under the terms of the GNU General Public License as published by
%% the Free Software Foundation, either version 3 of the License, or
%% (at your option) any later version.
%% This program is distributed in the hope that it will be useful,
%% but WITHOUT ANY WARRANTY; without even the implied warranty of
%% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
%% GNU General Public License for more details.
%% You should have received a copy of the GNU General Public License
%% along with this program.  If not, see <http://www.gnu.org/licenses/>.

    %% ctrRelSphereSUBs = DIM_SEARCHLIGHT_SPHERE(vox,rad)
    % create sphere for searchlight

    %% notes
    % based on searchlightMapping_fMRI.m (the MRC RSA-toolbox)

    %% function
	voxSize_mm          = [vox,vox,vox];
	searchlightRad_mm   = rad;
	rad_vox             = searchlightRad_mm./voxSize_mm;
	minMargin_vox       = floor(rad_vox);
	[x,y,z]             = meshgrid(-minMargin_vox(1):minMargin_vox(1),-minMargin_vox(2):minMargin_vox(2),-minMargin_vox(3):minMargin_vox(3));
	sphere              = ((x*voxSize_mm(1)).^2+(y*voxSize_mm(2)).^2+(z*voxSize_mm(3)).^2)<=(searchlightRad_mm^2);
	sphereSize_vox      = [size(sphere),ones(1,3-ndims(sphere))];
	[sphereSUBx,sphereSUBy,sphereSUBz]=ind2sub(sphereSize_vox,find(sphere));
	sphereSUBs          = [sphereSUBx,sphereSUBy,sphereSUBz];
	ctrSUB              = 0.5*sphereSize_vox + [.5 .5 .5];
	ctrRelSphereSUBs    = sphereSUBs-ones(size(sphereSUBs,1),1)*ctrSUB;
end
