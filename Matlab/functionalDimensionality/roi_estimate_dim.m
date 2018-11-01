function [subject_ID, test_run, winning_model, test_correlation] = roi_estimate_dim(data,res,subject_ID,full)
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

if islogical(res)
    % Skip pre-procesing...
    % Step 2: Evaluating all possible SVD (dimensional) models.
     output = svd_nested_crossval(data, subject_ID, full);
else
    % ...or Step 1: Data pre-processing
    % noise normalisation:
    n_sessions = size(data, 3);
    n_betas    = size(data,2);
    beta_norm  = nan(size(data));
    for i_session = 1:n_sessions
        cov_e = covdiag(res(:,:,i_session)');
        beta_norm(:,:,i_session) = ((data(:,:,i_session))' * cov_e^-.5)';
    end
    % remove voxel baseline:
    data_mc = beta_norm - repmat(mean(beta_norm, 2), 1,n_betas, 1);
    % Step 2: Evaluating all possible SVD (dimensional) models.
    output = svd_nested_crossval(data_mc, subject_ID, full);
end

subject_ID = cat(2,output{:,1});
test_run  = cat(2,output{:,2});
winning_model  = cat(2,output{:,3});
test_correlation  = cat(2,output{:,4});

end