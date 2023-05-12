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
def replace_values(dfg1, dfg2):
    """
    Replace edge values specified in a DFG by values from a (potentially bigger) DFG

    Parameters
    -----------
    dfg1
        First specified DFG (where values of edges should be replaces)
    dfg2
        Second specified DFG (from which values should be taken)

    Returns
    -----------
    dfg1
        First specified DFG with overrided values
    """
    for edge in dfg1:
        if edge in dfg2:
            dfg1[edge] = dfg2[edge]
    return dfg1
