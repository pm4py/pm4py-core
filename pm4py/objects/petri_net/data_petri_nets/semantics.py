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
from pm4py.objects.petri_net.sem_interface import Semantics
import re


security_pattern = re.compile(r'[.]|\\x[0-9a-fA-F]+')


class DataPetriNetSemantics(Semantics):
    def is_enabled(self, t, pn, m, **kwargs):
        """
        Verifies whether a given transition is enabled in a given Petri net and marking

        Parameters
        ----------
        :param t: transition to check
        :param pn: Petri net
        :param m: marking to check
        :param e: associated event (optional, as keyword argument)

        Returns
        -------
        :return: true if enabled, false otherwise
        """
        e = kwargs["e"] if "e" in kwargs else {}
        return is_enabled(t, pn, m, e)

    def execute(self, t, pn, m, **kwargs):
        """
        Executes a given transition in a given Petri net, the given data marking and the associated event

        Parameters
        ----------
        :param t: transition to execute
        :param pn: Petri net
        :param m: marking to use
        :param e: associated event (optional, as keyword argument)

        Returns
        -------
        :return: newly reached marking if :param t: is enabled, None otherwise
        """
        e = kwargs["e"] if "e" in kwargs else {}
        return execute(t, pn, m, e)

    def weak_execute(self, t, pn, m, **kwargs):
        """
        Executes a given transition in a given Petri net, the given data marking and the associated event,
        even if not fully enabled

        Parameters
        ----------
        :param t: transition to execute
        :param pn: Petri net
        :param m: marking to use
        :param e: associated event (optional, as keyword argument)

        Returns
        -------
        :return: newly reached marking
        """
        e = kwargs["e"] if "e" in kwargs else {}
        return weak_execute(t, m, e)

    def enabled_transitions(self, pn, m, **kwargs):
        """
        Returns a set of enabled transitions in a Petri net, the given data marking and the associated event

        Parameters
        ----------
        :param pn: Petri net
        :param m: marking of the pn
        :param e: associated event (optional, as keyword argument)

        Returns
        -------
        :return: set of enabled transitions
        """
        e = kwargs["e"] if "e" in kwargs else {}
        return enabled_transitions(pn, m, e)


def check_guard_safety(guard):
    """
    Checks the security of a guard before evaluating that

    Parameters
    ----------------
    guard
        Guard

    Returns
    ----------------
    safety
        True if the guard is safe to execute, False otherwise
    """
    return not security_pattern.search(guard)


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
        dct = {}
        for k in read_variables:
            dct[k] = None
        for k, v in data.items():
            dct[k] = v
        if check_guard_safety(guard):
            ret = eval(guard, dct)
            return ret
        return False
    except:
        # the guard could not be evaluated (for example, given missing data)
        return False



# 29/08/2021: the following methods have been incapsulated in the DataPetriNetSemantics class.
# the long term idea is to remove them. However, first we need to adapt the existing code to the new
# structure. Moreover, for performance reason, it is better to leave the code here, without having
# to instantiate a DataPetriNetSemantics object.
def is_enabled(t, pn, m, e):
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


def weak_execute(t, m, e):
    m_out = copy.copy(m)
    for a in t.in_arcs:
        m_out[a.source] -= a.weight
        if m_out[a.source] <= 0:
            del m_out[a.source]
    for a in t.out_arcs:
        m_out[a.target] += a.weight

    m_out.data_dict.update(e)

    return m_out


def enabled_transitions(pn, m, e):
    enabled = set()
    for t in pn.transitions:
        if is_enabled(t, pn, m, e):
            enabled.add(t)
    return enabled
