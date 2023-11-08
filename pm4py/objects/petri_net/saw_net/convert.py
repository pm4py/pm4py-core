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

from pm4py.objects.petri_net.saw_net.obj import StochasticArcWeightNet
from pm4py.objects.petri_net.stochastic.obj import StochasticPetriNet
from pm4py.objects.petri_net.saw_net.semantics import GlobalStochasticArcWeightNetSemantics as sawsem_global, LocalStochasticArcWeightNetSemantics as sawsem_local
from typing import Counter as TCounter, Tuple
from collections import deque

def convert_saw_net_to_stochastic_net_global_semantics(saw: StochasticArcWeightNet) -> StochasticPetriNet:
    sn = StochasticPetriNet()
    p_map = dict()
    for p in saw.places:
        p_new = StochasticPetriNet.Place(p.name, properties=p.properties)
        sn.places.add(p_new)
        p_map[p] = p_new
    
    a_sums = dict()
    for a in saw.arcs:
        a_sums[a] = 0
        for (w, v) in a.weight_distribution.items():
            a_sums[a] = a_sums[a] + v
        
    for t in saw.transitions:
        bindings = sawsem_global.all_legal_bindings(saw, t)
        for b in bindings:
            transition_weight = t.weight
            t_new = StochasticPetriNet.Transition('t'+str(len(sn.transitions)),t.label)
            sn.transitions.add(t_new)
            for (a,w) in b:
                a_new = StochasticPetriNet.Arc(t_new,p_map[a.target],w) if a.source == t else StochasticPetriNet.Arc(p_map[a.source],t_new,w)
                if a.source == t:
                    t_new.out_arcs.add(a_new)
                    p_map[a.target].in_arcs.add(a_new)
                else:
                    t_new.in_arcs.add(a_new)
                    p_map[a.source].out_arcs.add(a_new)
                sn.arcs.add(a_new)
                transition_weight = transition_weight * (a.weight_distribution[w] / a_sums[a])
            t_new.weight = transition_weight
    return sn, p_map


def convert_saw_net_to_stochastic_net_local_semantics(saw: StochasticArcWeightNet, marking: TCounter[StochasticArcWeightNet.Place]) -> Tuple[StochasticPetriNet,TCounter[StochasticArcWeightNet.Place]]:
    sn = StochasticPetriNet()
    open = deque()
    closed = set()
    markings = dict()
    markings[marking] = {p: StochasticPetriNet.Place(p.name+'-'+str(marking)) for p in marking if marking[p] > 0}
    for p in markings[marking]:
        sn.places.add(markings[marking][p])
    open.append(marking)
    while len(open) > 0:
        m = open.pop()
        for t in saw.transitions:
            if sawsem_local.is_enabled(saw,t,m):
                for b in sawsem_local.all_enabled_bindings(saw,t,m):
                    m_out = sawsem_local.fire(saw,b,m)
                    if m_out not in markings:
                        markings[m_out] = {p: StochasticPetriNet.Place(p.name+'-'+str(m_out)) for p in m_out if m_out[p] > 0}
                        for p in markings[m_out]:
                            sn.places.add(markings[m_out][p])                    
                    t_new = StochasticPetriNet.Transition(t.name + '-' + str(b), t.label, weight=t.weight * sawsem_local.amortized_priority(b)/sum([sawsem_local.amortized_priority(bb) for bb in sawsem_local.all_enabled_bindings(saw,t,m)]))
                    sn.transitions.add(t_new)
                    plcs_in = markings[m]
                    plcs_out = markings[m_out]
                    for p in m:
                        if m[p] > 0:
                            a = StochasticPetriNet.Arc(plcs_in[p],t_new,m[p])
                            plcs_in[p].out_arcs.add(a)
                            t_new.in_arcs.add(a)
                            sn.arcs.add(a)
                    for p in m_out:
                        if m_out[p] > 0:
                            a = StochasticPetriNet.Arc(t_new,plcs_out[p],m_out[p])
                            plcs_out[p].in_arcs.add(a)
                            t_new.out_arcs.add(a)
                            sn.arcs.add(a)
                    if m_out not in closed and m_out is not m:
                        open.append(m_out)
    return sn, {markings[marking][p]: marking[p] for p in marking}
