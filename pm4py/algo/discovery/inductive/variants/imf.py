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
from typing import TypeVar, Generic, Dict, Any, Optional

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL, IMDataStructureLog
from pm4py.algo.discovery.inductive.fall_through.empty_traces import EmptyTracesUVCL
from pm4py.algo.discovery.inductive.variants.abc import InductiveMinerFramework
from pm4py.algo.discovery.inductive.variants.instances import IMInstance
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.objects.dfg.obj import DFG
from copy import copy
from enum import Enum
from pm4py.util import exec_utils


T = TypeVar('T', bound=IMDataStructureLog)


class IMFParameters(Enum):
    NOISE_THRESHOLD = "noise_threshold"


class IMF(Generic[T], InductiveMinerFramework[T]):

    def instance(self) -> IMInstance:
        return IMInstance.IMf


class IMFUVCL(IMF[IMDataStructureUVCL]):
    def apply(self, obj: IMDataStructureUVCL, parameters: Optional[Dict[str, Any]] = None, second_iteration: bool = False) -> ProcessTree:
        noise_threshold = exec_utils.get_param_value(IMFParameters.NOISE_THRESHOLD, parameters, 0.0)

        empty_traces = EmptyTracesUVCL.apply(obj, parameters)
        if empty_traces is not None and empty_traces[1]:
            number_original_traces = sum(y for y in obj.data_structure.values())
            number_filtered_traces = sum(y for y in empty_traces[1][1].data_structure.values())

            if number_original_traces - number_filtered_traces > noise_threshold * number_original_traces:
                return self._recurse(empty_traces[0], empty_traces[1], parameters)
            else:
                obj = empty_traces[1][1]

        tree = self.apply_base_cases(obj, parameters)
        if tree is None:
            cut = self.find_cut(obj, parameters)
            if cut is not None:
                tree = self._recurse(cut[0], cut[1], parameters=parameters)
            if tree is None:
                if not second_iteration:
                    filtered_ds = self.__filter_dfg_noise(obj, noise_threshold)
                    tree = self.apply(filtered_ds, parameters=parameters, second_iteration=True)
                    if tree is None:
                        ft = self.fall_through(obj, parameters)
                        tree = self._recurse(ft[0], ft[1], parameters=parameters)
        return tree

    def __filter_dfg_noise(self, obj, noise_threshold):
        start_activities = copy(obj.dfg.start_activities)
        end_activities = copy(obj.dfg.end_activities)
        dfg = copy(obj.dfg.graph)
        outgoing_max_occ = {}
        for x, y in dfg.items():
            act = x[0]
            if act not in outgoing_max_occ:
                outgoing_max_occ[act] = y
            else:
                outgoing_max_occ[act] = max(y, outgoing_max_occ[act])
            if act in end_activities:
                outgoing_max_occ[act] = max(outgoing_max_occ[act], end_activities[act])
        dfg_list = sorted([(x, y) for x, y in dfg.items()], key=lambda x: (x[1], x[0]), reverse=True)
        dfg_list = [x for x in dfg_list if x[1] > noise_threshold * outgoing_max_occ[x[0][0]]]
        dfg_list = [x[0] for x in dfg_list]
        # filter the elements in the DFG
        graph = {x: y for x, y in dfg.items() if x in dfg_list}

        dfg = DFG()
        for sa in start_activities:
            dfg.start_activities[sa] = start_activities[sa]
        for ea in end_activities:
            dfg.end_activities[ea] = end_activities[ea]
        for act in graph:
            dfg.graph[act] = graph[act]

        return IMDataStructureUVCL(obj.data_structure, dfg)
