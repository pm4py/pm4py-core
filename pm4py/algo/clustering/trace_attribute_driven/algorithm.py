'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
from scipy.cluster.hierarchy import to_tree, linkage
from pm4py.statistics.attributes.log import get as attributes_filter
from pm4py.algo.clustering.trace_attribute_driven.merge_log import merge_log
from pm4py.algo.clustering.trace_attribute_driven.util import evaluation
from pm4py.objects.conversion.log import converter as log_converter
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd


class Variants(Enum):
    VARIANT_DMM_LEVEN = evaluation.eval_DMM_leven
    VARIANT_AVG_LEVEN = evaluation.eval_avg_leven
    VARIANT_DMM_VEC = evaluation.eval_DMM_variant
    VARIANT_AVG_VEC = evaluation.eval_avg_variant
    DFG = evaluation.dfg_dist


VARIANT_DMM_LEVEN = Variants.VARIANT_DMM_LEVEN
VARIANT_AVG_LEVEN = Variants.VARIANT_AVG_LEVEN
VARIANT_DMM_VEC = Variants.VARIANT_DMM_VEC
VARIANT_AVG_VEC = Variants.VARIANT_AVG_VEC
DFG = Variants.DFG

VERSIONS = {VARIANT_DMM_LEVEN, VARIANT_AVG_VEC, VARIANT_DMM_VEC, VARIANT_AVG_VEC, DFG}


def bfs(tree):
    queue = []
    output = []
    queue.append(tree)
    while queue:
        # element in queue is waiting to become root and splited into child
        # root is the first ele of queue
        root = queue.pop(0)
        if len(root['children']) > 0:
            name = [root['name']]
            for child in root['children']:
                queue.append(child)
                name.append(child['name'])
            output.append(name)

    return output


def apply(log: Union[EventLog, EventStream, pd.DataFrame], trace_attribute: str, variant=VARIANT_DMM_LEVEN, parameters: Optional[Dict[Any, Any]] = None) -> Any:
    """
    Apply the hierarchical clustering to a log starting from a trace attribute.

    MSc Thesis is available at: https://www.pads.rwth-aachen.de/global/show_document.asp?id=aaaaaaaaalpxgft&download=1
    Defense slides are available at: https://www.pads.rwth-aachen.de/global/show_document.asp?id=aaaaaaaaalpxgqx&download=1

    Parameters
    ----------------
    log
        Log
    trace_attribute
        Trace attribute to exploit for the clustering
    variant
        Variant of the algorithm to apply, possible values:
        - Variants.VARIANT_DMM_LEVEN (that is the default)
        - Variants.VARIANT_AVG_LEVEN
        - Variants.VARIANT_DMM_VEC
        - Variants.VARIANT_AVG_VEC
        - Variants.DFG

    Returns
    -----------------
    tree
        Hierarchical cluster tree
    leafname
        Root node
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    percent = 1
    alpha = 0.5

    list_of_vals = []
    list_log = []
    list_of_vals_dict = attributes_filter.get_trace_attribute_values(log, trace_attribute)

    list_of_vals_keys = list(list_of_vals_dict.keys())
    for i in range(len(list_of_vals_keys)):
        list_of_vals.append(list_of_vals_keys[i])

    for i in range(len(list_of_vals)):
        logsample = merge_log.log2sublog(log, list_of_vals[i], trace_attribute)
        list_log.append(logsample)

    y = exec_utils.get_variant(variant)(list_log, percent, alpha)

    Z = linkage(y, method='average')

    # Create dictionary for labeling nodes by their IDs

    id2name = dict(zip(range(len(list_of_vals)), list_of_vals))

    T = to_tree(Z, rd=False)
    d3Dendro = dict(children=[], name="Root1")
    merge_log.add_node(T, d3Dendro)

    leafname = merge_log.label_tree(d3Dendro["children"][0], id2name)
    d3Dendro = d3Dendro["children"][0]
    d3Dendro["name"] = 'root'
    tree = d3Dendro

    trilist = bfs(tree)
    trilist[0][0] = trilist[0][1] + '-' + trilist[0][2]

    rootlist = []
    for ele in trilist:
        rootlist.append(ele[0])

    return tree, leafname
