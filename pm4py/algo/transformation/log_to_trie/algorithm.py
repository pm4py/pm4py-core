from enum import Enum

from pm4py import util
from pm4py.objects.log.obj import EventLog
from pm4py.objects.trie.obj import Trie
from pm4py.statistics.variants.log import get as get_variants_log
from pm4py.statistics.variants.pandas import get as get_variants_pandas
from typing import Optional, Dict, Any, Union
import pandas as pd


class Parameters(Enum):
    ACTIVITY_KEY = util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY


def apply(log: Union[EventLog, pd.DataFrame], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Trie:
    parameters = parameters if parameters is not None else dict()

    if type(log) is pd.DataFrame:
        variants = get_variants_pandas.get_variants_set(log, parameters=parameters)
    else:
        variants = get_variants_log.get_variants(log, parameters=parameters)

    variants = list(variants)

    root = Trie()

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
