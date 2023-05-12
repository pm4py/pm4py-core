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
from collections import Counter


def equivalence(trace):
    """
    Get the equivalence relations given a list of activities

    Parameters
    --------------
    trace
        List activities

    Returns
    --------------
    rel
        Relations inside the trace
    """
    ret = list()
    freq = activ_freq(trace)
    for x in freq:
        for y in freq:
            if x != y and freq[x] == freq[y]:
                for i in range(freq[x]):
                    ret.append((x, y))
    return ret


def after(trace):
    """
    Get the after- relations given a list of activities

    Parameters
    --------------
    trace
        List activities

    Returns
    --------------
    rel
        After- inside the trace
    """
    return list((trace[i], trace[j]) for i in range(len(trace)) for j in range(len(trace)) if j > i)


def before(trace):
    """
    Get the before- relations given a list of activities

    Parameters
    --------------
    trace
        List activities

    Returns
    --------------
    rel
        Before- inside the trace
    """
    return list((trace[i], trace[j]) for i in range(len(trace)) for j in range(len(trace)) if j < i)


def combos(trace):
    """
    Get the combinations between all the activities of the trace relations given a list of activities

    Parameters
    --------------
    trace
        List activities

    Returns
    --------------
    rel
        Combos inside the trace
    """
    return set((x, y) for x in trace for y in trace if x != y)


def directly_follows(trace):
    """
    Get the directly-follows relations given a list of activities

    Parameters
    --------------
    trace
        List activities

    Returns
    --------------
    rel
        Directly-follows relations inside the trace
    """
    return list((trace[i], trace[i+1]) for i in range(len(trace)-1))


def activ_freq(trace):
    """
    Gets the frequency of activities happening in a trace

    Parameters
    --------------
    trace
        List activities

    Returns
    --------------
    freq
        Frequency of activities
    """
    return Counter(trace)


def get_trace_info(trace):
    """
    Technical method for conformance checking
    """
    return (equivalence(trace), after(trace), before(trace), combos(trace), directly_follows(trace), activ_freq(trace))
