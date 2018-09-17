def get_shortest_paths_from_trans(net, original_trans, spaths):
    """
    Get arcs that are shortest paths between a given
    visible transition and other visible transitions

    Parameters
    -----------
    net
        Petri net
    original_trans
        Original transition
    spaths
        Current dictionary of shortest paths

    Returns
    -----------
    spaths
        Updated shortest paths
    """
    already_visited_arcs = []
    already_visited_trans = []
    already_visited_places = []
    trans_list = [original_trans]
    while trans_list:
        trans = trans_list.pop(0)
        already_visited_trans.append(trans)
        for out_arc in trans.out_arcs:
            if not out_arc in already_visited_arcs:
                already_visited_arcs.append(out_arc)
                target_place = out_arc.target
                if not target_place in already_visited_places:
                    already_visited_places.append(target_place)
                    for place_out_arc in target_place.out_arcs:
                        if not place_out_arc in already_visited_places:
                            target_trans = place_out_arc.target
                            if not target_trans in already_visited_trans:
                                already_visited_trans.append(target_trans)
                                if target_trans.label:
                                    if not out_arc in spaths:
                                        spaths[out_arc] = set()
                                    if not place_out_arc in spaths:
                                        spaths[place_out_arc] = set()
                                    spaths[out_arc].add((original_trans.name, target_trans.name, 0))
                                    spaths[place_out_arc].add((original_trans.name, target_trans.name, 1))
                                trans_list.append(target_trans)
    return spaths

def get_shortest_paths(net):
    """
    Gets shortest paths between visible transitions in a Petri net

    Parameters
    -----------
    net
        Petri net

    Returns
    -----------
    spaths
        Shortest paths
    """
    spaths = {}
    for trans in net.transitions:
        if trans.label:
            spaths = get_shortest_paths_from_trans(net, trans, spaths)
    return spaths