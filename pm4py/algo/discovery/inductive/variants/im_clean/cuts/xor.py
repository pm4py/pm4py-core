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
from typing import Optional, Dict

import networkx as nx

import pm4py
from pm4py.algo.discovery.inductive.variants.im_clean import utils as im_utils
from pm4py.algo.discovery.inductive.variants.im_clean.d_types import DFG, Cut


def detect(dfg: DFG, alphabet: Dict[str, int]) -> Optional[Cut]:
    '''
    This method finds a xor cut in the dfg.
    Implementation follows function XorCut on page 188 of
    "Robust Process Mining with Guarantees" by Sander J.J. Leemans (ISBN: 978-90-386-4257-4)

    Basic Steps:
    1.) the dfg is transformed to its undirected equivalent.
    2.) we detect the connected components in the graph.
    3.) if there are more than one connected components, the cut exists and is non-minimal.

    Parameters
    ----------
    dfg
        input directly follows graph
    alphabet
        alphabet of the dfg

    Returns
    -------
        A list of sets of activities, i.e., forming a maximal xor cut
        None if no cut is found.

    '''
    nx_dfg = im_utils.transform_dfg_to_directed_nx_graph(dfg, alphabet)
    nx_und = nx_dfg.to_undirected()
    conn_comps = [nx_und.subgraph(c).copy() for c in nx.connected_components(nx_und)]
    if len(conn_comps) > 1:
        cuts = list()
        for comp in conn_comps:
            cuts.append(set(comp.nodes))
        return cuts
    else:
        return None


def project(log, groups, activity_key):
    # currently not 'noise' proof
    # assumes that no empty traces are in the log
    logs = list()
    for group in groups:
        logs.append(pm4py.filter_log(lambda t: t[0][activity_key] in group, log))
    return logs
