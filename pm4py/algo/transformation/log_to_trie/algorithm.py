from enum import Enum

from pm4py import util
from pm4py.objects.log.obj import EventLog
from pm4py.objects.trie.obj import Trie
from pm4py.statistics.variants.log import get as get_variants
from typing import Optional, Dict, Any, Union, Tuple


class Parameters(Enum):
    ACTIVITY_KEY = util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY


def apply(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Trie:
    parameters = parameters if parameters is not None else dict()
    root = Trie()
    variants = list(map(lambda v: v.split(','), get_variants.get_variants(log, parameters=parameters)))
    for variant in variants:
        trie = root
        for i, activity in enumerate(variant):
            match = False
            for c in trie.children:
                if c.label == activity:
                    trie = c
                    match = True
                    break
            if match:
                continue
            node = Trie(label=activity, parent=trie, depth=trie.depth + 1)
            trie.children.append(node)
            trie = node
            if i == len(variant) - 1:
                trie.final = True
    return root
