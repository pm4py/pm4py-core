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
from pm4py.objects.petri_net.sem_interface import Semantics
from pm4py.objects.petri_net.obj import ResetNet
from pm4py.objects.petri_net.obj import InhibitorNet


class InhibitorResetSemantics(Semantics):
    def is_enabled(self, t, pn, m, **kwargs):
        """
        Verifies whether a given transition is enabled in a given Petri net and marking

        Parameters
        ----------
        :param t: transition to check
        :param pn: Petri net
        :param m: marking to check

        Returns
        -------
        :return: true if enabled, false otherwise
        """
        return is_enabled(t, pn, m)

    def execute(self, t, pn, m, **kwargs):
        """
        Executes a given transition in a given Petri net and Marking

        Parameters
        ----------
        :param t: transition to execute
        :param pn: Petri net
        :param m: marking to use

        Returns
        -------
        :return: newly reached marking if :param t: is enabled, None otherwise
        """
        return execute(t, pn, m)

    def weak_execute(self, t, pn, m, **kwargs):
        """
        Execute a transition even if it is not fully enabled

        Parameters
        ----------
        :param t: transition to execute
        :param pn: Petri net
        :param m: marking to use

        Returns
        -------
        :return: newly reached marking if :param t: is enabled, None otherwise
        """
        return weak_execute(t, m)

    def enabled_transitions(self, pn, m, **kwargs):
        """
        Returns a set of enabled transitions in a Petri net and given marking

        Parameters
        ----------
        :param pn: Petri net
        :param m: marking of the pn

        Returns
        -------
        :return: set of enabled transitions
        """
        return enabled_transitions(pn, m)


# 29/08/2021: the following methods have been incapsulated in the InhibitorResetSemantics class.
# the long term idea is to remove them. However, first we need to adapt the existing code to the new
# structure. Moreover, for performance reason, it is better to leave the code here, without having
# to instantiate a InhibitorResetSemantics object.
def is_enabled(t, pn, m):
    if t not in pn.transitions:
        return False
    else:
        for a in t.in_arcs:
            if isinstance(a, InhibitorNet.InhibitorArc):
                if m[a.source] > 0:
                    return False
            elif isinstance(a, ResetNet.ResetArc):
                pass
            elif m[a.source] < a.weight:
                return False
    return True


def execute(t, pn, m):
    if not is_enabled(t, pn, m):
        return None

    m_out = copy.copy(m)
    for a in t.in_arcs:
        if isinstance(a, ResetNet.ResetArc):
            m_out[a.source] = 0
            del m_out[a.source]
        elif isinstance(a, InhibitorNet.InhibitorArc):
            pass
        else:
            m_out[a.source] -= a.weight
            if m_out[a.source] == 0:
                del m_out[a.source]

    for a in t.out_arcs:
        m_out[a.target] += a.weight

    return m_out


def weak_execute(t, m):
    m_out = copy.copy(m)
    for a in t.in_arcs:
        if isinstance(a, ResetNet.ResetArc):
            m_out[a.source] = 0
            del m_out[a.source]
        elif isinstance(a, InhibitorNet.InhibitorArc):
            pass
        else:
            m_out[a.source] -= a.weight
            if m_out[a.source] <= 0:
                del m_out[a.source]
    for a in t.out_arcs:
        m_out[a.target] += a.weight
    return m_out


def enabled_transitions(pn, m):
    enabled = set()
    for t in pn.transitions:
        if is_enabled(t, pn, m):
            enabled.add(t)
    return enabled
