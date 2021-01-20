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
from pm4py.objects.dfg.retrieval import log as log_calc


def apply(log, parameters=None):
    """
    Measure performance between couples of attributes in the DFG graph

    Parameters
    ----------
    log
        Log
    parameters
        Possible parameters passed to the algorithms:
            Parameters.AGGREGATION_MEASURE -> performance aggregation measure (min, max, mean, median)
            Parameters.ACTIVITY_KEY -> Attribute to use as activity
            Parameters.TIMESTAMP_KEY -> Attribute to use as timestamp

    Returns
    -------
    dfg
        DFG graph
    """
    return log_calc.performance(log, parameters=parameters)
