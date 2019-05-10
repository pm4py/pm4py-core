#from intervaltree import Interval
#from pandas import Timestamp
from intervaltree import Interval
from pandas import Timestamp

def get_distr_points(tree, parameters=None):
    if parameters is None:
        parameters = {}

    n_points = parameters["n_points"] if "n_points" in parameters else 3000

    int_begin = tree.begin()
    int_end = tree.end()

    interval = float((int_end - int_begin))/float(n_points)

    ret = []

    for i in range(n_points):
        x = int_begin + (0.5 + i) * interval
        y = tree[x]

        ret.append([x, len(y), set(eval(z.data)["CASEID"] for z in y)])

    all_intervals = tree[int_begin:int_end]

    for interval in all_intervals:
        i_begin = interval.begin
        i_end = interval.end
        x = (float(i_end) + float(i_begin))/2.0

        y = tree[x]
        ret.append([x, len(y), set(eval(z.data)["CASEID"] for z in y)])

    ret = sorted(ret, key=lambda x: x[0])

    return ret
