"""First experiment. 1D data."""

# Guilhere Franca <guifranca@gmail.com>
# Johns Hopkins University, Neurodata

import numpy as np
import multiprocessing as mp

import energy.data as data
import energy.eclust as eclust
import energy.initialization as initialization
import run_clustering
import plot

def sample_normal(m1, m2, s1, s2, n1, n2):
    return data.univariate_normal([m1, m2], [s1, s2], [n1, n2])

def sample_lognormal(m1, m2, s1, s2, n1, n2):
    return data.univariate_lognormal([m1, m2], [s1, s2], [n1, n2])


class Clustering1D:

    def __init__(self):
        # parameters for distributions
        self.m1 = 0
        self.m2 = 5
        self.s1 = 1
        self.s2 = 2
        self.distr = 'normal' # should be normal or lognormal
        self.numpoints = range(50, 100, 20)
        self.experiments = 100 # number of experiments (Markov samples)

    def get_sample(self, n):
        n1, n2 = np.random.multinomial(n, [0.5, 0.5])
        if self.distr == 'normal':
            X, z = sample_normal(self.m1, self.m2, self.s1, self.s2, n1, n2)
        elif self.distr == 'lognormal':
            X, z = sample_lognormal(self.m1, self.m2, self.s1, self.s2, n1, n2)
        else:
            raise ValueError("Clustering 1D, unknown distribution to sample.")
        return X, z

    def run(self):
        k = 2
        ncols = 3 + 1 # number of clustering methods + 1
        table = np.zeros((self.experiments*len(self.numpoints), ncols))
        count = 0
        for i, n in enumerate(self.numpoints):
            for ne in range(self.experiments):
                X, z = self.get_sample(n)
                Y = np.array([[x] for x in X])
                #G = eclust.kernel_matrix(Y, lambda x, y: np.linalg.norm(x-y))
                table[count, 0] = n
                table[count, 1] = run_clustering.energy1D(X, z)
                table[count, 2] = run_clustering.kmeans(k, Y, z, run_times=5)
                table[count, 3] = run_clustering.gmm(k, Y, z, run_times=5)
                #table[count, 4] = run_clustering.energy_hartigan(k, X, G, z,
                #                            init="k-means++", run_times=3)
                #table[count, 4] = run_clustering.energy_hartigan(k, Y, G, z,
                #                    init="spectral")
                count += 1
        return table

###############################################################################
## the functions below need to be customized according
## to the experiment

def make_plot(*data_files):
    table = []
    for f in data_files:
        t = np.loadtxt(f, delimiter=',')
        t[:,0] = np.array([int(D) for D in t[:,0]])
        table.append(t)
    table = np.concatenate(table)

    ## customize plot below ##
    p = plot.ErrorBar()
    p.xlabel = r'$\#$ points'
    p.legends = [r'$\mathcal{E}^{1D}$-clustering', r'$k$-means', 'GMM']
    p.colors = ['b', 'r', 'g']
    p.lines = ['-', '-', '-']
    #p.output = './experiments_figs/1D_normal.pdf'
    p.output = './experiments_figs/1D_lognormal.pdf'
    p.bayes = 0.88
    p.xlim = [10,800]
    #p.loc = (0.55,0.45)
    p.make_plot(table)

def gen_data(fname):
    ## choose the range for each worker ##
    n_array = [range(10,400,20),
               range(400,700,20),
               range(700,760,20),
               range(760,820,20)]
    jobs = []
    for i, n in enumerate(n_array):
        p = mp.Process(target=worker, args=(n, fname%i))
        jobs.append(p)
        p.start()

def worker(numpoints, fname):
    """Used for multiprocessing. i is the index of the file, each process
    will generate its own output file.
    
    """
    e = Clustering1D()
   
    ## Need to change these parameters below by hand according to
    ## the experiment
    e.m1 = 1.5
    e.m2 = 0
    e.s1 = 0.3
    e.s2 = 1.5
    #e.distr = 'normal'
    e.distr = 'lognormal'
    e.experiments = 100
    
    e.numpoints = numpoints
    table = e.run()
    np.savetxt(fname, table, delimiter=',')
    

###############################################################################
if __name__ == '__main__':
    #fname = './experiments_data/experiment_1D_normal_%i.csv'
    fname = './experiments_data/experiment_1D_lognormal_%i.csv'
    #gen_data(fname)
    make_plot(fname%0, fname%1, fname%2, fname%3)
