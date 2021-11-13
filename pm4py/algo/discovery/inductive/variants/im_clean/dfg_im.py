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
from enum import Enum

from pm4py.algo.discovery.inductive.variants.im_clean.cuts import sequence as sequence_cut, xor as xor_cut, \
    concurrency as concurrent_cut, loop as loop_cut
from pm4py.algo.discovery.inductive.variants.im_clean.utils import __filter_dfg_on_threshold, __flower, DfgSaEaActCount
from pm4py.objects.dfg.utils import dfg_utils
from pm4py.objects.process_tree import obj as pt
from pm4py.util import constants


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


def __imd(dfg_sa_ea_actcount, threshold, root, remove_noise=False):
    tree = __imd_internal(dfg_sa_ea_actcount, threshold, root, remove_noise)
    return tree


def __imd_internal(dfg_sa_ea_actcount, threshold, root, remove_noise=False):
    alphabet = dfg_sa_ea_actcount.act_count.keys()
    if len(dfg_sa_ea_actcount.act_count) > 0 and len(dfg_sa_ea_actcount.dfg) == 0:
        return __base_case(dfg_sa_ea_actcount, root)
    if threshold > 0 and remove_noise:
        dfg = __filter_dfg_on_threshold(dfg_sa_ea_actcount.dfg, dfg_sa_ea_actcount.end_activities, threshold)
        dfg_sa_ea_actcount = DfgSaEaActCount(dfg, dfg_sa_ea_actcount.start_activities,
                                             dfg_sa_ea_actcount.end_activities, dfg_sa_ea_actcount.act_count)
        alphabet = dfg_sa_ea_actcount.act_count.keys()
    pre, post = dfg_utils.get_transitive_relations(dfg_sa_ea_actcount.dfg, alphabet)
    cut = sequence_cut.detect(alphabet, pre, post)
    if cut is not None:
        dfgs, skippable = sequence_cut.project_dfg(dfg_sa_ea_actcount, cut)
        return __add_subdfgs(dfgs, skippable, threshold, root, pt.Operator.SEQUENCE)
    cut = xor_cut.detect(dfg_sa_ea_actcount.dfg, alphabet)
    if cut is not None:
        dfgs, skippable = xor_cut.project_dfg(dfg_sa_ea_actcount, cut)
        return __add_subdfgs(dfgs, skippable, threshold, root, pt.Operator.XOR)
    cut = concurrent_cut.detect(dfg_sa_ea_actcount.dfg, alphabet, dfg_sa_ea_actcount.start_activities,
                                dfg_sa_ea_actcount.end_activities)
    if cut is not None:
        dfgs, skippable = concurrent_cut.project_dfg(dfg_sa_ea_actcount, cut)
        return __add_subdfgs(dfgs, skippable, threshold, root, pt.Operator.PARALLEL)
    cut = loop_cut.detect(dfg_sa_ea_actcount.dfg, alphabet, dfg_sa_ea_actcount.start_activities,
                          dfg_sa_ea_actcount.end_activities)
    if cut is not None:
        dfgs, skippable = loop_cut.project_dfg(dfg_sa_ea_actcount, cut)
        return __add_subdfgs(dfgs, skippable, threshold, root, pt.Operator.LOOP)
    if threshold > 0 and not remove_noise:
        return __imd(dfg_sa_ea_actcount, threshold, root, remove_noise=True)
    return __flower(alphabet, root)


def __add_subdfgs(dfgs, skippable, threshold, root, operator):
    i = 0
    parent = pt.ProcessTree(operator=operator, parent=root)
    while i < len(dfgs):
        if skippable[i]:
            this_parent = pt.ProcessTree(operator=pt.Operator.XOR, parent=parent)
            parent.children.append(this_parent)
            skip = pt.ProcessTree(parent=this_parent)
            this_parent.children.append(skip)
        else:
            this_parent = parent
        this_parent.children.append(__imd(dfgs[i], threshold, this_parent))
        i = i + 1
    return parent


def __base_case(dfg, root):
    parent = pt.ProcessTree(operator=pt.Operator.XOR, parent=root)
    for act in dfg.act_count:
        node = pt.ProcessTree(label=act, parent=parent)
        parent.children.append(node)
    return parent
