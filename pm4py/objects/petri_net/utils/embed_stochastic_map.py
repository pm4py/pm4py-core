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
from pm4py.util.constants import STOCHASTIC_DISTRIBUTION


def apply(smap, parameters=None):
    """
    Embed the stochastic map into the Petri net

    Parameters
    ---------------
    smap
        Stochastic map
    parameters
        Possible parameters of the algorithm

    Returns
    ---------------
    void
    """
    if parameters is None:
        parameters = {}

    for t in smap:
        t.properties[STOCHASTIC_DISTRIBUTION] = smap[t]


def extract(net, parameters=None):
    """
    Extract the stochastic map from the Petri net

    Parameters
    --------------
    net
        Petri net
    parameters
        Possible parameters of the algorithm

    Returns
    --------------
    void
    """
    if parameters is None:
        parameters = {}

    smap = {}

    for t in net.transitions:
        smap[t] = t.properties[STOCHASTIC_DISTRIBUTION]

    return smap
