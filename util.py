import pickle

##############################################################################
def from_pkl(fn, fp='./pkl/', fx='.p'):
    ''' Returns the contents of a pickled file as a Python object. '''
    with open(fp+fn+fx, 'rb') as f:
        result = pickle.load(f)
        f.close()
    return result
##############################################################################
def to_pkl(obj, fn, fp='./pkl/', fx='.p'):
    ''' Stores the contents of a Python object in a pickled file. '''
    with open(fp+fn+fx, 'wb') as f:
        pickle.dump(obj, f)
        f.close()
##############################################################################
