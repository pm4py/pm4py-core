from pm4py.algo.task_mining.grouping import factory as grouping_factory
from pm4py.algo.task_mining.tasks import factory as task_assignation_factory
from pm4py.algo.task_mining.sequence_mining import factory as seq_min_factory
from pm4py.algo.task_mining.sequence_clustering import factory as seq_clust_factory
from pm4py.algo.task_mining.sequence_scoring import score


def apply(stream, parameters=None):
    """
    Applies task mining to the given stream (BPM 2019 method)

    Parameters
    -------------
    stream
        Event stream
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
    if parameters is None:
        parameters = {}
    grouped_stream = grouping_factory.apply(stream, parameters=parameters)
    new_grouped_stream, all_labels = task_assignation_factory.apply(grouped_stream, parameters=parameters)
    frequents, frequents_label, frequents_encodings, frequents_occurrences = seq_min_factory.apply(new_grouped_stream,
                                                                                                   all_labels,
                                                                                                   parameters=parameters)
    communities = seq_clust_factory.apply(frequents_label, frequents_encodings, parameters=parameters)
    sequence_scores = score.apply(frequents_occurrences, parameters=parameters)

    processes = []
    for cluster in communities:
        processes.append([])
        for i in cluster:
            if len(frequents[i]) > 1 and len(frequents_occurrences[i]) > 0:
                label = [all_labels[x] for x in frequents[i]]
                processes[-1].append({"label": label, "score": sequence_scores[i], "no_occurrences": len(frequents_occurrences[i]), "events": frequents_occurrences[i]})
        processes[-1] = sorted(processes[-1], key=lambda x: x["score"], reverse=True)
    return processes
