from enum import Enum

from pm4py import util
from pm4py.objects.log.obj import EventLog
from pm4py.objects.trie.obj import Trie
from pm4py.statistics.variants.log import get as get_variants
from typing import Optional, Dict, Any, Union, Tuple
from pm4py.util import variants_util, constants
import pandas as pd
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    ACTIVITY_KEY = util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY


def apply(log: Union[EventLog, pd.DataFrame], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Trie:
    parameters = parameters if parameters is not None else dict()
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)
    root = Trie()
    variants = get_variants.get_variants(log, parameters=parameters)
    if variants_util.VARIANT_SPECIFICATION == variants_util.VariantsSpecifications.STRING:
        variants = list(map(lambda v: v.split(constants.DEFAULT_VARIANT_SEP), variants))
    else:
        variants = list(variants)

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
