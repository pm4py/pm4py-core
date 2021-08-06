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
import copy
from pm4py.objects.petri_net import properties as petri_properties


def evaluate_guard(guard, read_variables, data):
    """
    Evaluates a data Petri net guard given the current data

    Parameters
    ------------------
    guard
        Guard
    read_variables
        Read variables

    Returns
    ------------------
    boolean
        Boolean value
    """
    guard = guard.replace("&&", " and ").replace("||", " or ").replace("true", "True").replace("false", "False")
    try:
        for k in read_variables:
            exec(str(k)+"=None")
        for k, v in data.items():
            exec(str(k)+"="+str(v))
        return eval(guard)
    except:
        # the guard could not be evaluated (for example, given missing data)
        return False


def is_enabled(t, pn, m, e):
    """
    Verifies whether a given transition is enabled in a given Petri net and marking

    Parameters
    ----------
    :param t: transition to check
    :param pn: Petri net
    :param m: marking to check
    :param e: associated event

    Returns
    -------
    :return: true if enabled, false otherwise
    """

    if t not in pn.transitions:
        return False
    else:
        for a in t.in_arcs:
            if m[a.source] < a.weight:
                return False

    if petri_properties.TRANS_GUARD in t.properties:
        guard = t.properties[petri_properties.TRANS_GUARD]
        read_variables = t.properties[petri_properties.READ_VARIABLE] if petri_properties.READ_VARIABLE in t.properties else []
        data = copy.copy(m.data_dict)
        data.update(e)
        evaluate_guard(guard, read_variables, data)

    return True


def execute(t, pn, m, e):
    """
    Executes a given transition in a given Petri net, the given data marking and the associated event

    Parameters
    ----------
    :param t: transition to execute
    :param pn: Petri net
    :param m: marking to use
    :param e: associated event

    Returns
    -------
    :return: newly reached marking if :param t: is enabled, None otherwise
    """

    if not is_enabled(t, pn, m, e):
        return None

    m_out = copy.copy(m)
    for a in t.in_arcs:
        m_out[a.source] -= a.weight
        if m_out[a.source] == 0:
            del m_out[a.source]

    for a in t.out_arcs:
        m_out[a.target] += a.weight

    m_out.data_dict.update(e)

    return m_out


def enabled_transitions(pn, m, e):
    """
    Returns a set of enabled transitions in a Petri net, the given data marking and the associated event

    Parameters
    ----------
    :param pn: Petri net
    :param m: marking of the pn
    :param e: associated event

    Returns
    -------
    :return: set of enabled transitions
    """
    enabled = set()
    for t in pn.transitions:
        if is_enabled(t, pn, m, e):
            enabled.add(t)
    return enabled
