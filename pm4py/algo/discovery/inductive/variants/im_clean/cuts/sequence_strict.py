import itertools
import sys
from pm4py.algo.discovery.inductive.variants.im_clean.cuts import sequence as seq_cut


def skippable(p: int, dfg, start, end, groups) -> bool:
    '''
    This method implements the function SKIPPABLE as defined on page 233 of 
    "Robust Process Mining with Guarantees" by Sander J.J. Leemans (ISBN: 978-90-386-4257-4)
    The function is used as a helper function for the strict sequence cut detection mechanism, which detects
    larger groups of skippable activities.
    '''
    for i, j in itertools.product(range(0, p), range(p+1, len(groups))):
        for a, b in itertools.product(groups[i], groups[j]):
            if (a, b) in dfg:
                return True
    for i in range(p+1, len(groups)):
        for a in groups[i]:
            if a in start:
                return True
    for i in range(0, p):
        for a in groups[i]:
            if a in end:
                return True
    return False


def detect(alphabet, trp, trs, dfg, start, end):
    '''
    This method implements the strict sequence cut as defined on page 233 of 
    "Robust Process Mining with Guarantees" by Sander J.J. Leemans (ISBN: 978-90-386-4257-4)
    The function merges groups that together can be skipped.

    Parameters
    ----------
    alphabet
        characters occurring in the dfg
    trp
        dictionary mapping activities to their (transitive) predecessors, according to the DFG
    transitive_successors
        dictionary mapping activities to their (transitive) successors, according to the DFG
    dfg 
        direcly follows graph
    start
        collection of start activities
    end
        colleciton of end activities

    Returns
    -------
        A list of sets of activities, i.e., forming a non-maximal sequence cut (allowing for smarter skips)
        None if no cut is found.
    '''
    C = seq_cut.detect(alphabet, trp, trs)
    if C is not None:
        mf = [-1* sys.maxsize if len(G.intersection(start)) > 0 else sys.maxsize for G in C ]
        mt = [sys.maxsize if len(G.intersection(end)) > 0 else -1 * sys.maxsize for G in C]
        cmap = _construct_alphabet_cluster_map(C)
        for (a, b) in dfg:
            mf[cmap[b]] = min(mf[cmap[b]], cmap[a])
            mt[cmap[a]] = max(mt[cmap[a]], cmap[b])

        for p in range(0, len(C)):
            if skippable(p, dfg, start, end, C):
                q = p - 1
                while q >= 0 and mt[q] <= p:
                    C[p] = C[p].union(C[q])
                    C[q] = set()
                    q -= 1
                q = p + 1
                while q < len(mf) and mf[q] >= p:
                    C[p] = C[p].union(C[q])
                    C[q] = set()
                    q += 1
        return list(filter(lambda g: len(g) > 0, C))
    return None

def _construct_alphabet_cluster_map(C):
    map = dict()
    for i in range(0, len(C)):
        for a in C[i]:
            map[a] = i
    return map
