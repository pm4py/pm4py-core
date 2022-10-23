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
from abc import ABC
from typing import TypeVar, Generic, Optional

from pm4py.algo.discovery.inductive.dtypes.im_dfg import InductiveDFG
from pm4py.objects.dfg.obj import DFG
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UVCL

T = TypeVar('T')


class IMDataStructure(ABC, Generic[T]):
    """
    The IMDataStructure is a helper class that unifies all possible data structures (typically logs or dfgs) that can
    be used for the classical Inductive Miner. The generic TypeVar 'T' is supposed to be the underlying data object
    used, and, should always be able to construct a DFG object. For example, T can be a dataframe, some other
    object representing an event log or a DFG itself.
    """

    def __init__(self, obj: T):
        self._obj = obj

    @property
    def dfg(self) -> DFG:
        pass

    @property
    def data_structure(self) -> T:
        return self._obj


class IMDataStructureLog(IMDataStructure[T], ABC, Generic[T]):
    """
    Generic class intended to represent that any subclass carries information that is captured in an event log.
    """


class IMDataStructureUVCL(IMDataStructureLog[UVCL]):
    """
    Log-Based data structure class that represents the event log as a 'Univariate Variant Compressed Log (UVCL)'
    """

    def __init__(self, obj: UVCL, dfg: Optional[DFG] = None):
        super().__init__(obj)
        if dfg is None:
            self._dfg = comut.discover_dfg_uvcl(self._obj)
        else:
            self._dfg = dfg

    @property
    def dfg(self) -> DFG:
        return self._dfg


class IMDataStructureDFG(IMDataStructure[InductiveDFG]):
    """
    DFG-Based data structure class
    """

    @property
    def dfg(self) -> DFG:
        return self._obj.dfg
