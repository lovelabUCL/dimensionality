function output = svd_nested_crossval(data,subject_ID,full)
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

n_beta = size(data,2);
n_session = size(data,3);
n_comp = n_beta-1;

if full
    winning_model = NaN([n_session-1, n_session,1]);
    test_correlation = NaN([n_session-1,n_session,1]);
    test_run = NaN([n_session-1,n_session,1]);
    rmat = NaN([n_comp,n_session-1,n_session]);
else
    winning_model = NaN([n_session,1]);
    test_correlation = NaN([n_session,1]);
    test_run = NaN([n_session,1]);
    rmat = NaN([n_comp,n_session-1,n_session]);
end
    

% Step 2: for each possible test-set, run n-1 validation runs
for i_test = 1:n_session
    data_val = data;
    data_test = data_val(:,:,i_test);
    data_val(:,:,i_test) = [];

    % Step 2: run validation
    for j_val  = 1:n_session -1
        data_val_train = data_val(:,:,setdiff(1:n_session-1,j_val));
        % Step 2: Factorize training data by SVD:
        [Uval,Sval,Vval] = make_components(data_val_train);
        for comp = 1:n_comp
            % Step 2: Set "comp" components to zero and correlate with validation set.
            rmat(comp,j_val,i_test) = reconstruct(Uval,Sval,Vval,comp,data_val(:,:,j_val));
        end
        
        if full % use dim estimate of each j_val
            test_run(j_val,i_test) = i_test;
            % Step 2: Pick the dimensionality with the highest correlelation.
            rvec = rmat(:,j_val,i_test);
            winning_model(j_val,i_test) = find(rvec==max(rvec));
            % Step 2: SVD and reconstruction of averaged training and validation data.
            [U,S,V] = make_components(data_val);
            test_correlation(j_val,i_test) = reconstruct(U,S,V,winning_model(j_val,i_test),data_test(:));
        end
    end
    if ~ full % choose best dim estimate by averaging over j_val
        test_run(i_test) = i_test;
        % Step 2: Mean Fischer z-transform.
        meanr = mean(atanh(rmat(:,:,i_test)),2);
        % Step 2: Pick the dimensionality with the highest correlelation.
        winning_model(i_test) = find(meanr==max(meanr));
        % Step 2: SVD and reconstruction of averaged training and validation data.
        [U,S,V] = make_components(data_val);
        test_correlation(i_test) = reconstruct(U,S,V,winning_model(i_test),data_test(:));
    end

end

output = {subject_ID, test_run, winning_model, test_correlation};
