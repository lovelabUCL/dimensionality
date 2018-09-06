function [] = dimensionality_demo(filename,opt_varname)

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

for dim = 1:dimensions
    disp(sprintf('dimension: %d',dim));
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
        disp(sprintf('\t \t mean best correlation: %f',mean_router));
        disp(sprintf('\t \t mean highest correlation: %f',mean_ralter));
    end
end
