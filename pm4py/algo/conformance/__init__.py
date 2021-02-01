from pm4py.algo.conformance import alignments, tokenreplay, log_skeleton, footprints, temporal_profile

import sys
# this package is available only for Python >= 3.6
if sys.version_info >= (3, 6):
    from pm4py.algo.conformance import tree_alignments
