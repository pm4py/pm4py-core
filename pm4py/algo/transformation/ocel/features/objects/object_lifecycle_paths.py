from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Adds for each object an one-hot-encoding of the paths performed in its lifecycle

    Parameters
    -----------------
    ocel
        OCEL
    parameters
        Parameters of the algorithm

    Returns
    -----------------
    data
        Values of the added features
    feature_names
        Names of the added features
    """
    if parameters is None:
        parameters = {}

    ordered_objects = list(ocel.objects[ocel.object_id_column])
    lifecycle = ocel.relations.groupby(ocel.object_id_column)[ocel.event_activity].agg(list).to_dict()

    data = []
    paths = {}
    all_paths = set()
    for obj in lifecycle:
        paths[obj] = []
        lobj = lifecycle[obj]
        for i in range(len(lobj)-1):
            path = lobj[i]+"##"+lobj[i+1]
            paths[obj].append(path)
            all_paths.add(path)

    all_paths = sorted(list(all_paths))
    feature_names = ["@@ocel_lif_path_"+str(x) for x in all_paths]

    for obj in ordered_objects:
        lif = paths[obj] if obj in paths else []
        data.append([])
        for p in all_paths:
            data[-1].append(len(list(x for x in lif if x == p)))

    return data, feature_names

