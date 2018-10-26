clear all;clc;
matfile = load('demo_data/sample_data.mat');
[vox, cond, sessions, subjects] = size(matfile.sample_data);
wholebrain_all = {};
for i = 1:subjects                   
    brain = matfile.sample_data(:,:,:,i);
    wholebrain_all{i} = brain;
end

% separate estimates for each run
full=0;
[bestn_all,r_outer_all,r_alter_all,test_tfce]=functional_dimensionality(wholebrain_all, ...
    'demo_data/sample_mask.img',full);

% average over runs:
for i_subject = 1:subjects
    mean_r_outer(:, i_subject) = mean(r_outer_all{i_subject},1);
    mean_r_alter(:, i_subject) = mean(r_alter_all{i_subject},1);
    mean_bestn(:, i_subject)   = mean(bestn_all{i_subject},1);
end

% point estimate of best dimensionality:
fprintf('bestn = %.2f\n',mean(mean_bestn(:)))


%%
