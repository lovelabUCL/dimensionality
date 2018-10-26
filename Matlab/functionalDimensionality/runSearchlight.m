function output = runSearchlight(voxel,u_sphere,mask,data,res)
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

%% notes
% based on searchlightMapping_fMRI.m (the MRC RSA-toolbox) & jbtools

% gets voxel-coordinates for searchlight and runs nested crossvalidation
% for SVD

% coordinates
[x,y,z] = ind2sub(mask.shape,voxel);

% subindices of voxels
u_xyz = repmat([x,y,z],[size(u_sphere,1) 1]) + u_sphere;
r_xyz = (u_xyz(:,1)<1 | u_xyz(:,1)>mask.shape(1) | u_xyz(:,2)<1 | u_xyz(:,2)>mask.shape(2) | u_xyz(:,3)<1 | u_xyz(:,3)>mask.shape(3));
u_xyz = u_xyz(~r_xyz,:);

% indices
ii_voxel = sub2ind(mask.shape,u_xyz(:,1),u_xyz(:,2),u_xyz(:,3));

% restrict searchlight to voxels inside mask.valid
f_voxel = mask.index(ii_voxel(mask.valid(ii_voxel)));

% number of voxels (return if not enough)
n = length(f_voxel);

n_beta = size(data, 2);
n_sessions = size(data, 3);

% Ensures that svd only runs if n_voxel > n_betas; otherwise return nan.
if n < n_beta+1, output = {nan(n_sessions, 1),nan(n_sessions, 1),nan(n_sessions, 1)}; return; end 

% get searchlight values
data_sl   = data(f_voxel,:,:);

% Ensure that we fail gracefully if the data contains nans.
if sum(isnan((data_sl(:)))) > 0, output = {nan(n_sessions, 1),nan(n_sessions, 1),nan(n_sessions, 1)}; return; end

% noise normalisation/prewhitening if desired;
% Step 1: Data pre-processing
if ~islogical(res)
    beta_norm  = nan(size(data_sl));
    sl_res = res(f_voxel,:,:);

    for i_session = 1:n_sessions
        cov_e = covdiag(sl_res(:,:,i_session)');
        beta_norm(:,:,i_session) = ((data_sl(:,:,i_session))' * cov_e^-.5)';
    end
    % remove voxel-baseline; needs to be done after prewhitening
    data_sl = beta_norm - repmat(mean(beta_norm, 2), 1,n_beta, 1);
end
    
% Step 2: Evaluating all possible SVD (dimensional) models.
output = ca_svd_nested_crossval_mean(data_sl);

end