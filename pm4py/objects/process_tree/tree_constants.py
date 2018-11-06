"""
Some constants useful in representing process trees
"""

from pm4py.objects.process_tree.nodes_objects import exclusive, loop, parallel, sequential

EXCLUSIVE_OPERATOR = "×"
PARALLEL_OPERATOR = "+"
SEQUENTIAL_OPERATOR = "→"
LOOP_OPERATOR = "⭯"

MAPPING = {EXCLUSIVE_OPERATOR: exclusive.Exclusive, PARALLEL_OPERATOR: parallel.Parallel,
           SEQUENTIAL_OPERATOR: sequential.Sequential, LOOP_OPERATOR: loop.Loop}
