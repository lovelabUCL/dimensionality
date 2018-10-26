function [bestn_all,r_outer_all, r_alter_all, test_tfce] = functional_dimensionality(wholebrain_all, mask, full,varargin)
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

% Load betas into wholebrain_all; 
% Set 'sphere' to perform searchlight, else ROI.
% Set 'spmfile' to perform noise normalisation/prewhitening if desired
% Residuals and beta estimates must not include any nans; mask with mask_mat

% output:
% bestn: for each run, the winning dimensionality
% r_outer: for each run, the correlation of the winnning dimensionality-reconstruction with the test data set
% r_alter: for each run, correlation achieved by a full-dimensional reconstruction with the test data set

preproc = inputParser;

addOptional(preproc,'sphere',-1,@isnumeric)
addParameter(preproc,'spmfile','',@ischar);
parse(preproc,varargin{:})


prewhiten = false;

spm_path = preproc.Results.spmfile;
if ~(spm_path == '')
    try
        SPM_file = load(spm_path);
        SPM = SPM_file.SPM;
        prewhiten = true;
    catch
        warning('Cant open the SPM file');
    end
end
    
mask_vol = spm_vol(mask);
mask_mat = spm_read_vols(mask_vol);

n_voxel   = sum(mask_mat(:));
n_subject = length(wholebrain_all);

for i_subject = 1:n_subject

    data = wholebrain_all{i_subject}; 
    data = data(logical(mask_mat(:)),:,:);
    n_sessions = size(data,3);
    
    if prewhiten
        % Load residuals.
        VRes = get_residuals_mat(SPM, NaN, mask_vol);
        res = VRes(:, logical(mask_mat(:)))';
        res = reshape(res, size(res, 1), size(res,2)/n_sessions, n_sessions);
        % data and res should have the same number of voxels and not include any nans.
    else
        res = false;
    end
    
    [bestn,r_outer, r_alter] = roi_estimate_dim(data, res,full);

    bestn_all{i_subject}   = bestn;
    r_outer_all{i_subject} = r_outer;
    r_alter_all{i_subject} = r_alter;
        
end

for i_subject = 1:n_subject
    mean_r_outer(:, i_subject) = mean(r_outer_all{i_subject},1);
    mean_r_alter(:, i_subject) = mean(r_alter_all{i_subject},1);
    mean_bestn(:, i_subject)   = mean(bestn_all{i_subject},1);
end

% Step 3: Determining statistical significance
if sphere > 0
    try
        vol_tfce = nan(size(mask_mat), 'double');
        vol_tfce = repmat(vol_tfce, 1,1,1,n_subject);
        mask_subj= repmat(mask_mat, 1,1,1,n_subject);
        vol_tfce(logical(mask_subj)) = mean_r_outer;
        test_tfce = matlab_tfce('onesample',1,vol_tfce);
    catch
        test_tfce = nan;
    end
else
    test_tfce = nan;
end


end
