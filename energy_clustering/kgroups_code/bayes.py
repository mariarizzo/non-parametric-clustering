"""Functions to compute Bayes errors."""

# Guilherme S. Franca <guifranca@gmail.com>
# Johns Hopkins University


from __future__ import division

from functools import partial
from scipy.optimize import minimize
from scipy.optimize import root
import numpy as np
import scipy.stats as stats
import scipy.integrate as integrate
import matplotlib.pyplot as plt

import data


def bayes_univariate_normal(mu1, mu2, sigma1, sigma2, 
                            num_times=10, num_points=1000, p=0.5):
    """Estimate Bayes' error for two-class normal distributions in 1D."""
    error = np.zeros(num_times)
    for i in range(num_times):
        q = 1-p
        n1, n2 = np.random.multinomial(num_points, [p,q])
        x1 = np.random.normal(mu1, sigma1, n1)
        x2 = np.random.normal(mu2, sigma2, n2)
    
        error1 = sum([1 for x in x1 
            if stats.norm.pdf(x,mu1,sigma1)-stats.norm.pdf(x,mu2,sigma2)<=0
        ])
        error2 = sum([1 for x in x2 
            if stats.norm.pdf(x,mu1,sigma1)-stats.norm.pdf(x,mu2,sigma2)>=0
        ])
        error[i] = p*error1/n1+q*error2/n2
    return 1-error.mean()

def integrate_univariate_normal(mu1, mu2, sigma1, sigma2, p=0.5):
    """Same as above but through numerical integration."""
    
    g1 = partial(stats.norm.pdf, loc=mu1, scale=sigma1)
    g2 = partial(stats.norm.pdf, loc=mu2, scale=sigma2)
    
    # make it visual to confirm
    #xs = np.arange(-10,20, 0.001)
    #y1s = np.array([g1(x) for x in xs])
    #y2s = np.array([g2(x) for x in xs])
    #y3s = np.array([np.abs(g1(x)-g2(x)) for x in xs])
    #plt.plot(xs, y1s)
    #plt.plot(xs, y2s)
    #plt.plot(xs, y3s)
    #plt.show()

    x0 = root(lambda x: g1(x) - g2(x), 1).x[0]
    
    # another way
    #cons = (
    #    {'type': 'ineq', 'fun': lambda x: x-1},
    #    {'type': 'ineq', 'fun': lambda x: -(x-2)},
    #)
    #x0 = minimize(lambda x: np.abs(g1(x)-g2(x)), x0=1, constraints=cons).x[0]
    q = 1-0.5
    e1 = integrate.quad(lambda x: p*g1(x), x0, np.inf)[0] 
    e2 = integrate.quad(lambda x: q*g2(x), -np.inf, x0)[0]
    accuracy = 1 - (e1+e2)
    return accuracy

def bayes_univariate_lognormal(mu1, mu2, sigma1, sigma2, 
                            num_times=10, num_points=1000, p=0.5):
    """Estimate Bayes' error for two-class normal distributions in 1D."""

    def lognorm(x, mu, sigma):
        return stats.lognorm.pdf(x, s=sigma, scale=np.exp(mu))
   
    error = np.zeros(num_times)
    for i in range(num_times):
        q = 1-p
        n1, n2 = np.random.multinomial(num_points, [p,q])
        x1 = np.random.lognormal(mu1, sigma1, n1)
        x2 = np.random.lognormal(mu2, sigma2, n2)
        
        error1 = sum([1 for x in x1 
                      if lognorm(x,mu1,sigma1)-lognorm(x,mu2,sigma2)<=0])
        error2 = sum([1 for x in x2 
                      if lognorm(x,mu1,sigma1)-lognorm(x,mu2,sigma2)>=0])
        error[i] = p*error1/n1+q*error2/n2
    return 1-error.mean()

def integrate_univariate_lognormal(mu1, mu2, sigma1, sigma2):
    """Same as above but through numerical integration."""
    
    def loggauss(x, mu, sigma):
        return stats.lognorm.pdf(x, s=sigma, scale=np.exp(mu))
    
    l1 = partial(loggauss, mu=mu1, sigma=sigma1)
    l2 = partial(loggauss, mu=mu2, sigma=sigma2)
    
    # make it visual to confirm
    #xs = np.arange(0,5, 0.001)
    #y1s = np.array([l1(x) for x in xs])
    #y2s = np.array([l2(x) for x in xs])
    #y3s = np.array([np.abs(l1(x)-l2(x)) for x in xs])
    #plt.plot(xs, y1s)
    #plt.plot(xs, y2s)
    #plt.plot(xs, y3s)
    #plt.show()

    x0 = root(lambda x: l1(x) - l2(x), 0.1).x[0]

    e1 = integrate.quad(lambda x: 0.5*l1(x), 0, x0)[0] 
    e2 = integrate.quad(lambda x: 0.5*l2(x), x0, 20)[0]
    accuracy = 1 - (e1+e2)
    return accuracy

def bayes_multivariate_normal(mu1, mu2, sigma1, sigma2, 
                              num_times=10, num_points=1000):
    """Estimate Bayes' error for two-class normal distributions in higher D."""
    
    def gauss(x, mu, sigma):
        return stats.multivariate_normal.pdf(x, mean=mu, cov=sigma)

    error = np.zeros(num_times)
    for i in range(num_times):
        p = 0.5
        q = 1-p
        n1, n2 = np.random.multinomial(num_points, [p,q])
        x1 = np.random.multivariate_normal(mu1, sigma1, n1)
        x2 = np.random.multivariate_normal(mu2, sigma2, n2)
    
        error1 = sum([1 for x in x1 
                      if gauss(x,mu1,sigma1)-gauss(x,mu2,sigma2)<=0])
        error2 = sum([1 for x in x2 
                      if gauss(x,mu1,sigma1)-gauss(x,mu2,sigma2)>=0])
        error[i] = p*error1/n1+q*error2/n2
    return 1-error.mean()

def bayes_multivariate_lognormal(mu1, mu2, sigma1, sigma2, 
                              num_times=10, num_points=1000):
    """Estimate Bayes' error for two-class lognormal 
       distributions in higher D."""
    
    def lognorm(x, mu, sigma):
        return stats.multivariate_normal.pdf(np.log(x), mean=mu, cov=sigma)

    error = np.zeros(num_times)
    for i in range(num_times):
        x1 = np.exp(np.random.multivariate_normal(mu1, sigma1, num_points))
        x2 = np.exp(np.random.multivariate_normal(mu2, sigma2, num_points))

        error1 = sum([1 for x in x1 
                      if lognorm(x,mu1,sigma1)-lognorm(x,mu2,sigma2)<=0])
        error2 = sum([1 for x in x2 
                      if lognorm(x,mu1,sigma1)-lognorm(x,mu2,sigma2)>=0])
        error[i] = error1+error2
    return error.mean()/(2*num_points)

    
#############################################################################
if __name__ == '__main__':

    m1 = 1.5
    s1 = 0.3
    m2 = 0
    s2 = 1.5
    #print bayes_univariate_normal(m1, m2, s1, s2, num_times=30,
    #                              num_points=10000, p=0.5)
    print bayes_univariate_lognormal(m1, m2, s1, s2, num_times=30,
                                  num_points=10000, p=0.5)
    #D = 25
    #m1 = np.zeros(D)
    #m2 = np.concatenate((0.7*np.ones(10), np.zeros(D-10)))
    #s1 = np.eye(D)
    #s2 = np.eye(D)
   
    #D = 50
    #d = 10
    #mu1 = np.zeros(D)
    #sigma1 = np.eye(D)
    #mu2 = np.concatenate((np.ones(d), np.zeros(D-d)))
    #sigma2 = np.eye(D)
    #for a in range(int(d/2)):
    #    sigma2[a,a] = a+1

    #D = 20
    #d = 5
    #mu1 = np.zeros(D)
    #sigma1 = 0.5*np.eye(D)
    #mu2 = np.concatenate((0.5*np.ones(d), np.zeros(D-d)))
    #sigma2 = np.eye(D)
    
    #print bayes_multivariate_lognormal(mu1, mu2, sigma1, sigma2, 
    #                                num_times=20, num_points=10000)

    #D = 50
    #d = 10
    #m1 = np.zeros(D)
    #m2 = np.concatenate((np.ones(d), np.zeros(D-d)))
    #s1 = np.eye(D)
    #s2 = np.eye(D)
    #for a in range(d):
    #    s1[a,a] = np.power(1/(a+1), 1)
    #for a in range(d):
    #    s2[a,a] = np.power(a+1, 1)
    #D = 11
    #d = 10
    #m1 = np.zeros(D)
    #m2 = np.concatenate((np.ones(d), np.zeros(D-d)))
    #s1 = np.eye(D)
    #s2_1 = np.array([1.367,  3.175,  3.247,  4.403,  1.249,                                             1.969, 4.035,   4.237,  2.813,  3.637])
    #s2 = np.diag(np.concatenate((s2_1, np.ones(D-d))))

