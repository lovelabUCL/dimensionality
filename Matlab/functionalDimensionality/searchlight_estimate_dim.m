function [bestn,r_outer, r_alter] = searchlight_estimate_dim(data, mask, res, sphere)
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

% run searchlight for a subject
% output:
% bestn: for each run, the winning dimensionality
% r_outer: for each run, the correlation of the winnning dimensionality-reconstruction with the test data set
% r_alter: for each run, correlation achieved by a full-dimensional reconstruction with the test data set


%% notes
% based on searchlightMapping_fMRI.m (the MRC RSA-toolbox)

%% function

% build sphere indices
u_sphere = dim_searchlight_sphere(3,sphere);

% get voxel
u_voxel = find(mask);
n_voxel = length(u_voxel);

mask = struct('valid',{mask});
mask.shape = size(mask.valid);
mask.index = nan(mask.shape);
mask.index(mask.valid) = 1:n_voxel;

% searchlight loop
output = arrayfun(@(i_voxel)runSearchlight(u_voxel(i_voxel),u_sphere,mask,data,res),1:n_voxel,'UniformOutput',false);

% results
output   = cat(1,output{:});
bestn    = cat(2,output{:,1});
r_outer  = cat(2,output{:,2});
r_alter  = cat(2,output{:,3});
end