from pm4py.algo.discovery.dfg.utils.dfg_utils import max_occ_all_activ, sum_start_activities_count, \
    sum_end_activities_count, sum_activities_count, max_occ_among_specif_activ


def verify_skip_transition_necessity(must_add_skip, initial_dfg, activities):
    """
    Utility functions that decides if the skip transition is necessary

    Parameters
    ----------
    must_add_skip
        Boolean value, provided by the parent caller, that tells if the skip is absolutely necessary
    initial_dfg
        Initial DFG
    activities
        Provided activities of the DFG
    """
    if must_add_skip:
        return True

    max_value = max_occ_all_activ(initial_dfg)
    start_activities_count = sum_start_activities_count(initial_dfg)
    end_activities_count = sum_end_activities_count(initial_dfg)
    max_val_act_spec = sum_activities_count(initial_dfg, activities)

    condition1 = start_activities_count > 0 and max_val_act_spec < start_activities_count
    condition2 = end_activities_count > 0 and max_val_act_spec < end_activities_count
    condition3 = max(start_activities_count, end_activities_count) <= 0 < max_val_act_spec < max_value
    condition = condition1 or condition2 or condition3

    #print("initial_dfg=",initial_dfg)
    #print("activities=",activities)
    #print("max_val_act_spec=",max_val_act_spec)
    #print("start_activities_count=",start_activities_count)
    #print(condition1, condition2, condition3, condition)
    #input()
    if condition:
        return True

    return False


def verify_skip_for_parallel_cut(dfg, children):
    """
    Verify skip necessity, specific version for parallel cuts

    Parameters
    -----------
    dfg
        Directly-follows graph
    children
        Child of the parallel cut

    Returns
    -----------
    must_add_skip
        Boolean value that is true if the skip shall be added
    """
    must_add_skip = False

    children_occurrences = []
    for child in children:
        child_occ = max_occ_among_specif_activ(dfg, child.activities)
        children_occurrences.append(child_occ)
    if children_occurrences:
        if not (children_occurrences[0] == children_occurrences[-1]):
            must_add_skip = True

    return must_add_skip
