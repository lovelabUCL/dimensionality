function [] = dimensionality_demo(filename,opt_varname)
%% “Copyright 2018, Christiane Ahlheim & Giles Greenway”
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

if nargin > 1
    varname = opt_varname;
else
    varname = 'sample_sim_data';
end

matfile = load(filename);

data = matfile.(convertCharsToStrings(varname));

[vox, cond, sessions, sims, subjects, dimensions, noise_levels] = size(data);

all_bestn = NaN(dimensions,sessions,sims,subjects,noise_levels);
all_router = NaN(dimensions,sessions,sims,subjects,noise_levels);
all_ralter = NaN(dimensions,sessions,sims,subjects,noise_levels);

[rep,sub,dim,noise]=ndgrid(1:sims,1:subjects,1:dimensions,1:noise_levels);

beta=[rep(:) sub(:) dim(:) noise(:)];

[sims j] = size(beta);
for i = 1:sims
    run = num2cell(beta(i,:));
    [r s d n] = run{:};
    cv=svd_nested_crossval(data(:,:,:,r,s,d,n));
    all_bestn(d,:,r,s,n)=cv{1};
    all_router(d,:,r,s,n)=cv{2};
    all_ralter(d,:,r,s,n)=cv{3};
end

ground_truth = [4 8 12];

for dim = 1:dimensions
    disp(sprintf('ground-truth dimensionality: %d', ground_truth(dim)));
    for noise = 1:noise_levels
        disp(sprintf('\t noise-level: %d',noise));
        bestn = all_bestn(dim,:,:,:,noise);
        router = all_router(dim,:,:,:,noise);
        ralter = all_ralter(dim,:,:,:,noise);
    
        flat_bestn = bestn(:);
        flat_router = router(:);
        flat_ralter = ralter(:);
        
        mean_bestn = mean(flat_bestn);
        mean_router = mean(flat_router);
        mean_ralter = mean(flat_ralter);
        
        disp(sprintf('\t \t mean best dimensionality: %f',mean_bestn));
        disp(sprintf('\t \t mean lowest correlation: %f',mean_router));
        disp(sprintf('\t \t mean highest correlation: %f',mean_ralter));
    end
end
