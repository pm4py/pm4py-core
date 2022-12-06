from pm4py.objects.petri_net.saw_net.obj import StochasticArcWeightNet
from pm4py.objects.petri_net.stochastic.obj import StochasticPetriNet
from pm4py.objects.petri_net.saw_net.semantics import StochasticArcWeightNetSemantics as sawsem

def convert_saw_net_to_stochastic_net(saw: StochasticArcWeightNet) -> StochasticPetriNet:
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
        bindings = sawsem.all_elegible_bindings(saw, t)
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
    return sn
                    
                    
                
            
            
    
    