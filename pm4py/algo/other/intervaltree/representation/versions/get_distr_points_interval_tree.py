#from intervaltree import Interval
#from pandas import Timestamp
#from datetime import datetime
from intervaltree import Interval
from pandas import Timestamp
from datetime import datetime


def get_distr_points(tree, parameters=None):
    """
    Get the distribution of interval overlapping in the interval tree
    (e.g. a point with 0 intersections has no intervals, a point with 1 intersection
    has 1 corresponding interval, a point with N intersections has N corresponding intervals

    Parameters
    -------------
    tree
        Interval tree
    parameters
        Parameters of the algorithm, including:
            n_points => Number of points to represent
    """
    if parameters is None:
        parameters = {}

    # custom attribute to query in interval data
    grouping_attr_in_data = parameters["grouping_attr_in_data"] if "grouping_attr_in_data" in parameters else None

    n_points = parameters["n_points"] if "n_points" in parameters else 3000

    int_begin = tree.begin()
    int_end = tree.end()

    interval = float((int_end - int_begin))/float(n_points)

    ret = []

    for i in range(n_points):
        x = int_begin + (0.5 + i) * interval
        y = tree[x]

        if grouping_attr_in_data:
            sett = set(eval(z.data)[grouping_attr_in_data] for z in y)
            ret.append([x, len(sett), sett])
        else:
            ret.append([x, len(y)])

    all_intervals = tree[int_begin:int_end]

    for interval in all_intervals:
        i_begin = interval.begin
        i_end = interval.end
        x = (float(i_end) + float(i_begin))/2.0

        y = tree[x]

        if grouping_attr_in_data:
            sett = set(eval(z.data)[grouping_attr_in_data] for z in y)
            ret.append([x, len(sett), sett])
        else:
            ret.append([x, len(y)])

    ret = sorted(ret, key=lambda x: x[0])

    return ret
