from sklearn.cluster import DBSCAN
import os
from pm4py.objects.log.log import EventStream


REMOVE_DUPLICATES = "remove_duplicates"
EQUIV_COLUMNS = "equiv_columns"
SPATIAL_COLUMN = "spatial_column"
WINDOW_NAME = "window_name"
FINAL_LABEL_IDX = "final_label_idx"
FINAL_LABEL = "final_label"
DEFAULT_EQUIV_COLUMNS = ["process_name", "classname"]
DEFAULT_SPATIAL_COLUMN = "event_position_rel"
DEFAULT_WINDOW_NAME = "window_name"
DEFAULT_FINAL_LABEL_IDX = "@@label_index"
DEFAULT_FINAL_LABEL = "@@label"

DBSCAN_EPS = "dbscan_eps"
DEFAULT_DBSCAN_EPS = 25.0


def longest_common_suffix(list_of_strings):
    """
    Finds the longest common suffix in a list of strings

    Parameters
    -------------
    list_of_strings
        List of strings

    Returns
    -------------
    longest_common
        Longest common suffix
    """
    reversed_strings = [' '.join(s.split()[::-1]) for s in list_of_strings]
    reversed_lcs = os.path.commonprefix(reversed_strings)
    lcs = ' '.join(reversed_lcs.split()[::-1])
    return lcs


def apply(grouped_stream, parameters=None):
    """
    Applies a grouping based on a set of equivalence columns and the distance between the clicks,
    in order to give eventually a label to each click

    Parameters
    ---------------
    grouped_stream
        Stream of events grouped (possibly, by resource and temporal constraints)
    parameters
        Parameters of the algorithm, including:
            remove_duplicates => Boolean that tells if duplicates shall be removed from the stream
            equiv_columns => Columns that are used for grouping, keeping all the events having
                an equivalent set of values
            spatial_column => Columns that contains the relative position of the mouse
            window_name => Column that contains the name of the window
            final_label_idx => Attribute that is going to store the index of the label
                associated to the event
            final_label => Attribute that is going to store the final event label
            dbscan_eps => Parameter of the clustering algorithm

    Returns
    ---------------
    new_grouped_stream
        New grouped stream
    all_labels
        All labels indexed
    """
    if parameters is None:
        parameters = {}

    equiv_columns = parameters[EQUIV_COLUMNS] if EQUIV_COLUMNS in parameters else DEFAULT_EQUIV_COLUMNS
    spatial_column = parameters[SPATIAL_COLUMN] if SPATIAL_COLUMN in parameters else DEFAULT_SPATIAL_COLUMN
    window_name = parameters[WINDOW_NAME] if WINDOW_NAME in parameters else DEFAULT_WINDOW_NAME
    final_label_idx = parameters[FINAL_LABEL_IDX] if FINAL_LABEL_IDX in parameters else DEFAULT_FINAL_LABEL_IDX
    final_label = parameters[FINAL_LABEL] if FINAL_LABEL in parameters else DEFAULT_FINAL_LABEL
    remove_duplicates = parameters[REMOVE_DUPLICATES] if REMOVE_DUPLICATES in parameters else True

    dbscan_eps = parameters[DBSCAN_EPS] if DBSCAN_EPS in parameters else DEFAULT_DBSCAN_EPS

    new_groups = {}

    for index, g in enumerate(grouped_stream):
        for index2, ev in enumerate(g):
            ev_features = "@@".join(ev[c] for c in equiv_columns)
            if ev_features not in new_groups:
                new_groups[ev_features] = []
            new_groups[ev_features].append((ev, index, index2))

    all_features = list(new_groups.keys())
    for fea in all_features:
        if len(new_groups[fea]) == 1:
            del new_groups[fea]

    all_labels = {}

    all_features = list(new_groups.keys())
    for fea in all_features:
        values = [eval(x[0][spatial_column]) for x in new_groups[fea]]
        db = DBSCAN(eps=dbscan_eps).fit(values)
        labels = db.labels_
        set_labels = list(set(labels))
        labels_corr = {}
        for x in set_labels:
            if not x == -1:
                labels_corr[x] = []
                for i in range(len(new_groups[fea])):
                    if labels[i] == x:
                        labels_corr[x].append(new_groups[fea][i])
        this_new_group = []
        for x in labels_corr:
            all_points = [eval(y[0][spatial_column]) for y in labels_corr[x]]
            centroid = " (%.1f, %.1f) " % (sum(x[0] for x in all_points)/len(all_points), sum(x[1] for x in all_points)/len(all_points))

            window_names = [y[0][window_name] for y in labels_corr[x]]
            wn_lp = os.path.commonprefix(window_names)
            wn_ls = longest_common_suffix(window_names)

            title = ""
            if len(wn_lp) > 0 or len(wn_ls) > 0:
                if len(wn_lp) >= len(wn_ls):
                    title = wn_lp
                else:
                    title = wn_ls

            e_cols_values = [" ".join(y[0][col] for col in equiv_columns) for y in labels_corr[x]][0]
            new_label = e_cols_values + centroid + title

            this_label_idx = len(all_labels)
            all_labels[this_label_idx] = new_label

            for y in labels_corr[x]:
                y[0][final_label_idx] = this_label_idx
                y[0][final_label] = new_label
                this_new_group.append(y)
        if len(this_new_group) > 1:
            new_groups[fea] = this_new_group
        else:
            del new_groups[fea]

    indexed_events = {}
    all_features = list(new_groups.keys())
    for fea in all_features:
        for ev, index, index2 in new_groups[fea]:
            if index not in indexed_events:
                indexed_events[index] = []
            indexed_events[index].append((index2, ev))

    ret_grouped_stream = []
    for index in indexed_events:
        ret_grouped_stream.append([y[1] for y in sorted(indexed_events[index], key=lambda x: x[0])])

    if remove_duplicates:
        for g in ret_grouped_stream:
            i = 1
            while i < len(g):
                if g[i][final_label] == g[i-1][final_label]:
                    del g[i]
                    continue
                i = i + 1
        i = 0
        while i < len(ret_grouped_stream):
            g = ret_grouped_stream[i]
            if len(g) <= 1:
                del ret_grouped_stream[i]
                continue
            i = i + 1

    return EventStream(ret_grouped_stream), all_labels
