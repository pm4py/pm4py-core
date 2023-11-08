from pm4py.objects.petri_net.obj import *
from pm4py.objects.petri_net.utils import petri_utils as pn_utils
from pm4py.objects.dcr.obj import Relations


def map_existing_transitions_of_copy_0(delta, copy_0, t, tapn) -> (PetriNet, PetriNet.Transition):
    trans = copy_0[delta]
    # if trans in tapn.transitions: # since this is a copy this cannot be checked here. trust me bro
    in_arcs = trans.in_arcs
    for arc in in_arcs:
        source = arc.source
        type = arc.properties['arctype'] if 'arctype' in arc.properties else None
        s_to_t = pn_utils.add_arc_from_to(source, t, tapn, type=type, with_check=True)
        s_to_t.properties['agemin'] = arc.properties['agemin'] if 'agemin' in arc.properties else None
        s_to_t.properties['transportindex'] = arc.properties['transportindex'] if 'transportindex' in arc.properties else None
    out_arcs = trans.out_arcs
    for arc in out_arcs:
        target = arc.target
        type = arc.properties['arctype'] if 'arctype' in arc.properties else None
        t_to_t = pn_utils.add_arc_from_to(t, target, tapn, type=type, with_check=True)
        t_to_t.properties['agemin'] = arc.properties['agemin'] if 'agemin' in arc.properties else None
        t_to_t.properties['transportindex'] = arc.properties['transportindex'] if 'transportindex' in arc.properties else None
    return tapn, t


def create_event_pattern_transitions_and_arcs(tapn, event, helper_struct, mapping_exceptions):
    inc_place = helper_struct[event]['places']['included']
    exec_place = helper_struct[event]['places']['executed']
    pend_places = helper_struct[event]['places']['pending']
    pend_exc_places = helper_struct[event]['places']['pending_excluded']
    i_copy = helper_struct[event]['trans_group_index']
    ts = []
    for t_name in set(helper_struct[event]['t_types']).intersection(set(['event','init'])):  # ['event','init'] - copy arcs:
        t = PetriNet.Transition(f'{t_name}_{event}{i_copy}', f'{t_name}_{event}{i_copy}_label')
        tapn.transitions.add(t)
        # this if statement handles self response exclude
        if event in mapping_exceptions.self_exceptions[frozenset([Relations.E.value, Relations.R.value])]:
            for pend_exc_place, _ in pend_exc_places:
                pn_utils.add_arc_from_to(t, pend_exc_place, tapn)

        pn_utils.add_arc_from_to(inc_place, t, tapn)
        # this if statement handles self exclude and self response exclude
        if not ((event in mapping_exceptions.self_exceptions[Relations.E.value]) or (
                event in mapping_exceptions.self_exceptions[frozenset([Relations.E.value, Relations.R.value])])):
            pn_utils.add_arc_from_to(t, inc_place, tapn)

        # this if statement handles self response
        if event in mapping_exceptions.self_exceptions[Relations.R.value]:
            for pend_place, _ in pend_places:
                pn_utils.add_arc_from_to(t, pend_place, tapn)

        if t_name.__contains__('init'):
            pn_utils.add_arc_from_to(t, exec_place, tapn)
            pn_utils.add_arc_from_to(exec_place, t, tapn, type='inhibitor')
        else:
            pn_utils.add_arc_from_to(t, exec_place, tapn)
            pn_utils.add_arc_from_to(exec_place, t, tapn)

        if t_name.__contains__('pend'):
            for pend_place, _ in pend_places:
                pn_utils.add_arc_from_to(pend_place, t, tapn)
        else:
            for pend_place, _ in pend_places:
                pn_utils.add_arc_from_to(pend_place, t, tapn, type='inhibitor')
        ts.append(t)
    for t_name in set(helper_struct[event]['t_types']).intersection(set(['initpend', 'pend'])):  # ['initpend','pend'] - copy transitions:
        for k in range(len(pend_places)):
            pend_place, e_prime = list(pend_places)[k]
            pend_exc_place, _ = list(pend_exc_places)[k]
            name = f'{t_name}_{event}_by_{e_prime}{i_copy}' if len(e_prime) > 0 else f'{t_name}_{event}{i_copy}'
            t = PetriNet.Transition(name, f'{name}_label')
            tapn.transitions.add(t)
            # this if statement handles self response exclude
            if event in mapping_exceptions.self_exceptions[frozenset([Relations.E.value, Relations.R.value])]:
                pn_utils.add_arc_from_to(t, pend_exc_place, tapn)

            pn_utils.add_arc_from_to(inc_place, t, tapn)
            # this if statement handles self exclude and self response exclude
            if not ((event in mapping_exceptions.self_exceptions[Relations.E.value]) or (
                    event in mapping_exceptions.self_exceptions[frozenset([Relations.E.value, Relations.R.value])])):
                pn_utils.add_arc_from_to(t, inc_place, tapn)

            # this if statement handles self response
            if event in mapping_exceptions.self_exceptions[Relations.R.value]:
                pn_utils.add_arc_from_to(t, pend_place, tapn)

            if t_name.__contains__('init'):
                pn_utils.add_arc_from_to(t, exec_place, tapn)
                pn_utils.add_arc_from_to(exec_place, t, tapn, type='inhibitor')
            else:
                pn_utils.add_arc_from_to(t, exec_place, tapn)
                pn_utils.add_arc_from_to(exec_place, t, tapn)

            if t_name.__contains__('pend'):
                pn_utils.add_arc_from_to(pend_place, t, tapn)
            else:
                pn_utils.add_arc_from_to(pend_place, t, tapn, type='inhibitor')
            ts.append(t)
    helper_struct[event]['trans_group_index'] += 1
    return tapn, ts


def get_expected_places_transitions_arcs(G):
    # 3^(conditions + milestones) * 2^((inc+exc)+(resp+no_resp))*2 for each event in relations
    expected_transitions = 0
    # 3*no of events
    expected_places = 4 * len(G['events'])
    # arcs:
    #   - events * 12
    #   - conditions * 9
    #   - milestones * 8
    #   - responses * 2
    #   - noResponses * 2
    #   - includes * 2
    #   - exludes * 2
    expected_arcs = 0

    for event in G['events']:
        expected_transitions += ((3 ** (len(G['conditionsFor'][event]) if event in G['conditionsFor'] else 0 +
                                                                                                           len(G[
                                                                                                                   'milestonesFor'][
                                                                                                                   event]) if event in
                                                                                                                              G[
                                                                                                                                  'milestonesFor'] else 0)) *
                                 (3 ** ((len(G['includesTo'][event]) if event in G['includesTo'] else 0 +
                                                                                                      len(G[
                                                                                                              'excludesTo'][
                                                                                                              event]) if event in
                                                                                                                         G[
                                                                                                                             'excludesTo'] else 0)) *
                                  (4 ** (len(G['responseTo'][event]) if event in G['responseTo'] else 0 +
                                                                                                      len(G[
                                                                                                              'noResponseTo'][
                                                                                                              event]) if event in
                                                                                                                         G[
                                                                                                                             'noResponseTo'] else 0)))) * 4

        expected_arcs += 2 ^ ((3 ^ (len(set(G['includesTo'][event] if event in G['includesTo'] else set()).union(
            set(G['excludesTo'][event] if event in G['excludesTo'] else set()))))) *
                              (4 ^ (len(set(G['responseTo'][event] if event in G['responseTo'] else set()).union(
                                  set(G['noResponseTo'][event] if event in G['noResponseTo'] else set()))))) *
                              (3 ^ ((len(set(G['conditionsFor'][event])) if event in G['conditionsFor'] else 0))) *
                              (3 ^ ((len(set(G['milestonesFor'][event])) if event in G['milestonesFor'] else 0))))

    expected_arcs += len(G['events']) * 24
    return expected_places, expected_transitions, expected_arcs
