'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
from pm4py.objects.dfg.utils.dfg_utils import max_occ_all_activ, sum_start_activities_count, \
    sum_end_activities_count, sum_activities_count, max_occ_among_specif_activ


def verify_skip_transition_necessity(must_add_skip, initial_dfg, dfg, activities):
    """
    Utility functions that decides if the skip transition is necessary

    Parameters
    ----------
    must_add_skip
        Boolean value, provided by the parent caller, that tells if the skip is absolutely necessary
    initial_dfg
        Initial DFG
    dfg
        Current DFG
    activities
        Provided activities of the DFG
    """
    if must_add_skip:
        return True

    NOISE_THRESH = 0.05

    max_value = max_occ_all_activ(initial_dfg)
    start_activities_count = sum_start_activities_count(initial_dfg)
    end_activities_count = sum_end_activities_count(initial_dfg)
    max_val_act_spec = sum_activities_count(initial_dfg, activities)

    condition1 = start_activities_count > 0 and max_val_act_spec < start_activities_count
    condition2 = end_activities_count > 0 and max_val_act_spec < end_activities_count
    condition3 = len(dfg) == 0 and max(start_activities_count, end_activities_count) < max_val_act_spec < max_value
    condition4 = max(start_activities_count,
                     end_activities_count) < max_value * NOISE_THRESH and max(start_activities_count,
                                                                              end_activities_count) <= max_val_act_spec < max_value
    condition5 = max(start_activities_count, end_activities_count) <= 0 < max_val_act_spec < max_value

    condition = condition1 or condition2 or condition3 or condition4 or condition5

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

    max_children_occurrences = []
    sum_activities_count_list = []

    for child in children:
        max_child_occ = max_occ_among_specif_activ(dfg, child.activities)
        sum_acti_count = sum_activities_count(dfg, child.activities, enable_halving=False)
        max_children_occurrences.append(max_child_occ)
        sum_activities_count_list.append(sum_acti_count)
    if max_children_occurrences:
        if not max_children_occurrences[0] == max_children_occurrences[-1]:
            #and not sum_activities_count_list[0] == sum_activities_count_list[-1]:
            must_add_skip = True

    return must_add_skip
