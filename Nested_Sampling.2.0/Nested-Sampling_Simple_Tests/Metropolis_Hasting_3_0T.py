########################Import Modules##########################################
import numpy as np
from numba import jit , prange
import copy
#####################################
def MH_acceptance(loglikelihood_new,Prior_new,loglikelihood_old,Prior_old):

    """ Metropolis Hasting Acceptance Criteria

    Parameters
    -----------------

    loglikelihood_new : scalar
                        The loglikelihood value of the new sample

    Prior_new          :scalar
                        The Prior value of the new sample

    loglikelihood_old  :scalar
                        The logLikelihood value of the old(current) sample

    Prior_old          :scalar
                        The Prior value of the old(current) sampled

    -------------------
    Output :  0.0 or 1.0
            0.0 for rejected sample or 1.0 for accepted sample"""

    try:
        loglikelihood_new = float(loglikelihood_new)
        Prior_new = float(Prior_new)
        loglikelihood_old = float(loglikelihood_old)
        Prior_old        = float(Prior_old)
    except TypeError:
        raise TypeError('Please check input values, either integers or floats')


    #Acceptance ratio

    logR_likelihood = (loglikelihood_new - loglikelihood_old )

    try:
        np.seterr(all='ignore')
        R = np.exp(logR_likelihood)*(Prior_new/Prior_old)

    except ZeroDivisionError:
        raise ZeroDivisionError('Please check division by zero')

    #Generate a uniform random Number
    u = np.random.uniform()

    #Acceptance criteria
    if (R > u):

        #Accept new sample
        return 1.0

    else: return 0.0 #reject sample




#####################          Main mcmc     ##########################################################

#@jit(nonpython=True, parallel=True)
def MH_mcmc(loglikelihood_func,Prior_func,theta,args_loglike,args_prior,mcmc_steps,stepsize):
    """ Metropolis Hasting MCMC Algorithm

    Parameters

    --------------------

    loglikelihood_func : function
                        The logLikelihood function

    Prior_func         : function
                        The Prior function

    theta              : scalar or array
                        Initial sample to do mcmc from

    args_loglike       :array or list
                        extra arguments for the loglikelihood function

    args_prior       :array or list
                        extra arguments for the Prior function

    mcmc_steps         : scalar,int
                        The number of mcmc runs

    stepsize           : scalar
                        The jump length of a new sample

    -------------------

    Return
    ------------------

    chain_sample        : array
                         Samples from the mcmc chain

    chain_loglikelihood : array
                         Loglikelihood values of each sample

    chain_prior         : array
                        prior values of each sample

    Acceptance_ratio    : scalar
                        Acceptance ratio of the mcmc chain
    """

    naccept = 0      #count number of accepted samples
    nreject = 0     #count number of rejected samples

    #Store samples
    chain_sample = np.zeros((mcmc_steps,len(theta)))
    chain_loglikelihood = np.array([])
    chain_prior = np.array([])


    # Do mcmc on the random survivor
    for mcmci in prange(mcmc_steps):
        #Generate new sample by adding a random stepsize from a normal distribution centred at 0

        New_theta = theta + np.random.normal(0,stepsize)

        #Compute Likelihood and prior of New_theta

        loglikelihood_new = loglikelihood_func(New_theta,args_loglike)
        Prior_new         = Prior_func(New_theta,args_prior)

        #Compute Likelihood and prior of old sample (theta)

        loglikelihood_old = loglikelihood_func(theta,args_loglike)
        Prior_old         = Prior_func(theta,args_prior)


        #Take a decision to accept of reject ne wsample (1.0 for accept and 0.0 for reject)
        Decision = MH_acceptance(loglikelihood_new,Prior_new,loglikelihood_old,Prior_old)

        if Decision == 1.0 :  #if it was accepted
            #move to new sample
            theta = New_theta

            #Record new sample details
            chain_sample[mcmci] = New_theta
            chain_loglikelihood = np.append(chain_loglikelihood,loglikelihood_new)
            chain_prior         = np.append(chain_prior,Prior_new)

            naccept += 1

        else:
            #Reject the new sample and stay at the old sample (theta)
            theta = theta

            #Record the details of the current position (old sample) sample

            chain_sample[mcmci] = New_theta
            chain_loglikelihood = np.append(chain_loglikelihood,loglikelihood_old)
            chain_prior         = np.append(chain_prior,Prior_old)
            nreject += 1
    #Calculate the Acceptance ratio

    Acceptance_ratio = naccept/mcmc_steps

    return chain_sample , chain_loglikelihood ,chain_prior ,Acceptance_ratio
