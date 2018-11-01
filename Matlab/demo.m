clear all; close all; clc;

matfile = load('demo_data/sample_data.mat');
[vox, cond, sessions, subjects] = size(matfile.sample_data);
wholebrain_all = {};
subject_IDs=[];
for i = 1:subjects                   
    brain = matfile.sample_data(:,:,:,i);
    wholebrain_all{i} = brain;
    subject_IDs = [subject_IDs i];
end

% select 'full' or 'mean' option:
%   - full=0: estimate best dimensionality by averaging over inner CV loop. (as
%     in paper)
%   - full=1: return separate estimates for each inner CV loop. 
full = 1; 

% separate estimates for each run:
[subject_IDs, test_runs, winning_models, test_correlations]=functional_dimensionality(wholebrain_all, ...
    'demo_data/sample_mask.img',subject_IDs,full);

% average over runs:
median_winning_model = median(winning_models);
median_test_correlation = median(test_correlations);

% point estimate of best dimensionality:
fprintf('winning model overall = %.2f\n',median(median_winning_model(:)))

% write results to CSV file:
csvwrite('demo_output.csv', [subject_IDs, test_runs, winning_models, test_correlations])