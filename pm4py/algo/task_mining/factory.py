from pm4py.algo.task_mining.versions import bpm2019

BPM2019 = "bpm2019"

VERSIONS = {BPM2019: bpm2019.apply}


def apply(stream, variant=BPM2019, parameters=None):
    """
    Applies task mining to the given stream (BPM 2019 method)

    Parameters
    -------------
    stream
        Event stream
    variant
        Variant of the algorithm to use, possible values: bpm2019
    parameters
        Parameters (for the BPM 2019 method):
            resource_group_column => The column that is associated to the resource, and is used to firstly
                group the stream
            equiv_columns => List of columns that shall be equal in order for two successive events to belong to
                the same group
            time_delay => The delay that is considered for grouping two successive events into the
                same group
            remove_duplicates => Boolean that tells if duplicates shall be removed from the stream
            spatial_column => Columns that contains the relative position of the mouse
            window_name => Column that contains the name of the window
            final_label_idx => Attribute that is going to store the index of the label
                associated to the event
            final_label => Attribute that is going to store the final event label
            dbscan_eps => Parameter of the clustering algorithm
            nc => numbers of clusters
            p1 => weight of the first term
            p2 => weight of the second term

    Returns
    -------------
    (For the BPM 2019 method)
    A list containing the different processes found by clustering the frequent itemsets.
    The itemsets belonging to a cluster, depending on the clustering features, should describe similar steps.
    For each itemset, a score and the list of all corresponding subsets of the original stream
    that are corresponding to the itemset is returned.
    """
    return VERSIONS[variant](stream, parameters=parameters)
