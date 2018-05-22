function [bestn,r_outer, r_alter, test_tfce] = searchlight_estimate_dim(wholebrain_all, spm_path, mask_path, sphere, varargin)
%% ???Copyright 2018, Christiane Ahlheim???
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

preproc = inputParser;

addParameter(preproc,'residuals',false,@islogical);
addParameter(preproc,'prewhiten',false,@islogical);
parse(preproc,varargin{:});

SPM_file = load(spm_path);
SPM = SPM_file.SPM;

mask_vol = spm_vol(mask_path);
mask_mat = spm_read_vols(mask_vol);

n_voxel   = sum(mask_mat(:));
n_subject = length(wholebrain_all);

for i_subject = 1:n_subject

    data = wholebrain_all{i_subject}; 
    data = data(logical(mask_mat(:)),:,:);
    n_sessions = size(data,3);
    
    if preproc.Results.residuals
        VRes = get_residuals_mat(SPM, NaN, mask_vol);
        res = VRes(:, logical(mask_mat(:)))';
        res = reshape(res, size(res, 1), size(res,2)/n_sessions, n_sessions);
        % data and res should have the same number of voxels and not include any nans.
    else
        res = false;
    end
    
    [bestn,r_outer, r_alter] = searchlight_estimate_dim(data, logical(mask_mat), res, sphere);

    bestn_all{i_subject}   = bestn;
    r_outer_all{i_subject} = r_outer;
    r_alter_all{i_subject} = r_alter;
        
end

for i_subject = 1:n_subject
    mean_r_outer(:, i_subject)= mean(r_outer_all{i_subject},1);
    mean_r_alter(:, i_subject)= mean(r_alter_all{i_subject},1);
    mean_bestn(:, i_subject)  = mean(bestn_all{i_subject},1);
end
