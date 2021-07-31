# Helper Functions for RC Data Analyses
# Sean Griffin
import _pickle as cPickle
import numpy as np
##############################################################################

def from_pkl(fn, fp='./pkl/', fx='.p'):
    ''' Returns the contents of a pickled file as a Python object. '''
    with open(fp+fn+fx, 'rb') as f:
        result = cPickle.load(f)
        f.close()
    return result

##############################################################################

def to_pkl(obj, fn, fp='./pkl/', fx='.p'):
    ''' Stores the contents of a Python object in a pickled file. '''
    with open(fp+fn+fx, 'wb') as f:
        cPickle.dump(obj, f)
        f.close()

##############################################################################

def in_rc(input_MTS, RESCOM, n_drop=0, bidir=False):
    ''' Wrapper for sending MTS into a RC and receiving its state history. '''
    res_states = RESCOM.get_states(input_MTS, n_drop=n_drop, bidir=bidir)
    return res_states

##############################################################################

def one_in_rc(input_MTS, RESCOM):
    ''' Wrapper for sending a single MTS sample into a RC and receiving
        its reaction.
    '''
    result = RESCOM.single_input(input_MTS)
    return result

##############################################################################

def tricksy(rstates, limit):
    ''' Given a RC state matrix, square values of its second half. '''
    rstates_f = rstates[:,:,:limit]
    rstates_s = rstates[:,:,limit:]
    rstates_p = np.power(rstates_s, 2)
    new_rstates = np.concatenate((rstates_f, rstates_p), axis=2)
    return new_rstates

##############################################################################

def rmse(predictions, targets):
    ''' Return the root mean squared error between two TS. '''
    return np.sqrt(((predictions - targets) ** 2).mean())

##############################################################################
