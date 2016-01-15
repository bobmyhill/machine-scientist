"""This test verifies that, for a simple sampling process (i.e. with
small formulas, and few variables, parameters and operations, so that
the sampling is exhaustive) with no data, the frequency with which a
certain formula is visited is proportional to its probability (that
is, that the sampler samples from the equilibrium distribution).

"""

import sys
from numpy import exp
from pprint import pprint

sys.path.append('..')
from mcmc import Tree

DEGCORRECT = True

t = Tree(
    ops={'+' : 2, 'sin': 1},
    prior_par={'Nopi_+' : 0, 'Nopi_sin' : 0},
)
"""
t = Tree(
    parameters=[],
    ops={'+' : 2},
    prior_par={'Nopi_+' : 0},
)
"""

t.max_size = 7

count, energy, cannonical, representatives = {}, {}, {}, {}
for rep in range(1000000):
    t.mcmc_step(degcorrect=DEGCORRECT)
    print >> sys.stderr, \
        rep+1, t, t.E, t.get_energy(degcorrect=DEGCORRECT), t.n_commute
    if abs(t.E - t.get_energy(degcorrect=DEGCORRECT)) > 1.e-8:
        raise KKError
    can = t.cannonical()
    try:
        count[str(t)] += 1
    except KeyError:
        count[str(t)] = 1
        energy[str(t)] = t.get_energy(degcorrect=DEGCORRECT)
        cannonical[str(t)] = can
    if can not in representatives:
        representatives[can] = {}
    try:
        representatives[can][str(t)] += 1
    except KeyError:
        representatives[can][str(t)] = 1


with open('test1_out1.tmp', 'w') as outf:
    for f in count:
        print >> outf, exp(-energy[f]), count[f], \
            cannonical[f].replace(' ', ''), str(f).replace(' ', '')

with open('test1_out2.tmp', 'w') as outf:
    for c in representatives:
        for s in representatives[c]:
            print >> outf, representatives[c][s], c, s