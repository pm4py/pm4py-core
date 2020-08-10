from pm4py.algo.conformance import alignments, tokenreplay, log_skeleton, footprints

import sys
# this package is available only for Python >= 3.5
if sys.version_info >= (3, 5):
    from pm4py.algo.conformance import tree_alignments
