def write_xes(log, file_path):
    """
    Exports a XES log

    Parameters
    --------------
    log
        Event log
    file_path
        Destination path

    Returns
    -------------
    void
    """
    from pm4py.objects.log.exporter.xes import exporter as xes_exporter
    xes_exporter.apply(log, file_path)


def write_csv(log, file_path):
    """
    Exports a CSV log

    Parameters
    ---------------
    log
        Event log
    file_path
        Destination path

    Returns
    --------------
    void
    """
    from pm4py.objects.log.exporter.csv import exporter as csv_exporter
    csv_exporter.apply(log, file_path)


def write_petri_net(petri_net, initial_marking, final_marking, file_path):
    """
    Exports a (composite) Petri net object

    Parameters
    ------------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    file_path
        Destination path

    Returns
    ------------
    void
    """
    from pm4py.objects.petri.exporter import exporter as petri_exporter
    petri_exporter.apply(petri_net, initial_marking, file_path, final_marking=final_marking)


def write_process_tree(tree, file_path):
    """
    Exports a process tree

    Parameters
    ------------
    tree
        Process tree
    file_path
        Destination path

    Returns
    ------------
    void
    """
    from pm4py.objects.process_tree.exporter import exporter as tree_exporter
    tree_exporter.apply(tree, file_path)


def write_dfg(dfg, start_activities, end_activities, file_path):
    """
    Exports a DFG

    Parameters
    -------------
    dfg
        DFG
    start_activities
        Start activities
    end_activities
        End activities
    file_path
        Destination path

    Returns
    ------------
    void
    """
    from pm4py.objects.dfg.exporter import exporter as dfg_exporter
    dfg_exporter.apply(dfg, file_path,
                       parameters={dfg_exporter.Variants.CLASSIC.value.Parameters.START_ACTIVITIES: start_activities,
                                   dfg_exporter.Variants.CLASSIC.value.Parameters.END_ACTIVITIES: end_activities})
