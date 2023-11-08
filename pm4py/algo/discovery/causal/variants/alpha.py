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
"""
This module contains code that allows us to compute a causal graph, according to the alpha miner.
It expects a dictionary of the form (activity,activity) -> num of occ.
A causal relation holds between activity a and b, written as a->b, if dfg(a,b) > 0 and dfg(b,a) = 0.
"""
from typing import Dict, Tuple


def apply(dfg: Dict[Tuple[str, str], int]) -> Dict[Tuple[str, str], int]:
    """
    Computes a causal graph based on a directly follows graph according to the alpha miner

    Parameters
    ----------
    dfg: :class:`dict` directly follows relation, should be a dict of the form (activity,activity) -> num of occ.

    Returns
    -------
    causal_relation: :class:`dict` containing all causal relations as keys (with value 1 indicating that it holds)
    """
    causal_alpha = {}
    for (f, t) in dfg:
        if dfg[(f, t)] > 0:
            if (t, f) not in dfg:
                causal_alpha[(f, t)] = 1
            elif dfg[(t, f)] == 0:
                causal_alpha[(f, t)] = 1
    return causal_alpha
