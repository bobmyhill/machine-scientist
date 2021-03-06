import sys
import numpy as np
from scipy.stats import sem
from sklearn import cross_validation
from sympy import sympify, latex
from optparse import OptionParser

sys.path.append('..')
from mcmc import Tree
from iodata import *

sys.path.append('../Prior')
from fit_prior import read_prior_par


# -----------------------------------------------------------------------------
def parse_options():
    """Parse command-line arguments.

    """
    parser = OptionParser(usage='usage: %prog [options] DATASET MODELSTR')
    parser.add_option("-p", "--priorpar", dest="pparfile", default=None,
                      help="Use priors from this file (default: no priors)")
    return parser

# -----------------------------------------------------------------------------
def cross_val(t, method='kfold', k=2):
    x, y = t.x, t.y
    if method == 'lko':
        ttsplit = cross_validation.LeavePOut(len(y), k)
    elif method == 'kfold':
        ttsplit = cross_validation.KFold(len(y), n_folds=k)
    else:
        raise ValueError
    serr, aerr = [], []
    for train_index, test_index in ttsplit:
        xtrain, xtest = x.iloc[train_index], x.iloc[test_index]
        ytrain, ytest = y.iloc[train_index], y.iloc[test_index]
        tt = Tree(x=xtrain, y=ytrain, from_string=str(t))
        ypred = tt.predict(xtest)
        serr.append(np.mean((ytest - ypred)**2))
        aerr.append(np.mean(np.abs(ytest - ypred)))
    return serr, aerr


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    parser = parse_options()
    opt, args = parser.parse_args()

    dset = args[0]
    modelstr = args[1]

    data, x, y = read_data(dset)

    t = Tree(from_string=modelstr)
    t.x, t.y = x, y
    if opt.pparfile:
        t.prior_par = read_prior_par(opt.pparfile)
    sse = t.get_sse(fit=True)
    bic = t.get_bic(reset=True, fit=False)
    serr, aerr = cross_val(t, method='lko', k=1)

    # Output
    print 'Dataset: ', dset
    print 'Model:   ', t
    print 'LaTeX:   ', latex(sympify(str(t).replace('_a', 'a')))

    print 'SSE:     ', sse
    print 'RMSE:    ', np.sqrt(sse / float(len(y)))
    print 'BIC:     ', bic

    print 'LOO-RMSE:', np.sqrt(np.mean(serr))
    print 'LOO-MSE:  %g+-%g' % (np.mean(serr), sem(serr))
    print 'LOO-MAE:  %g+-%g' % (np.mean(aerr), sem(aerr))

    if opt.pparfile:
        print 'Prior c: ', t.prior_par
        print '-log(P): ', t.get_energy(degcorrect=False)
        
