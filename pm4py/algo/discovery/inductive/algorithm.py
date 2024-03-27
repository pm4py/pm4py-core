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
from typing import Optional, Dict, Any, Union

import pandas as pd

from pm4py import util as pmutil
from pm4py.algo.discovery.inductive.dtypes.im_dfg import InductiveDFG
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL, IMDataStructureDFG
from pm4py.algo.discovery.inductive.variants.im import IMUVCL
from pm4py.algo.discovery.inductive.variants.imf import IMFUVCL
from pm4py.algo.discovery.inductive.variants.imd import IMD
from pm4py.algo.discovery.inductive.variants.instances import IMInstance
from pm4py.objects.dfg.obj import DFG
from pm4py.objects.log.obj import EventLog
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.objects.process_tree.utils import generic as pt_util
from pm4py.objects.process_tree.utils.generic import tree_sort
from pm4py.util import constants
import warnings
from pm4py.util import exec_utils
from pm4py.util import xes_constants as xes_util
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UVCL


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY


class Variants(Enum):
    IM = IMInstance.IM
    IMf = IMInstance.IMf
    IMd = IMInstance.IMd


def apply(obj: Union[EventLog, pd.DataFrame, DFG, UVCL], parameters: Optional[Dict[Any, Any]] = None, variant=Variants.IM) -> ProcessTree:
    if parameters is None:
        parameters = {}
    ack = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_util.DEFAULT_NAME_KEY)
    tk = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_util.DEFAULT_TIMESTAMP_KEY)
    cidk = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, pmutil.constants.CASE_CONCEPT_NAME)

    process_tree = ProcessTree()
    if type(obj) is DFG:
        if variant is not Variants.IMd:
            if constants.SHOW_INTERNAL_WARNINGS:
                warnings.warn('Inductive Miner Variant requested for DFG artefact is not IMD, resorting back to IMD')
        imd = IMD(parameters)
        idfg = InductiveDFG(dfg=obj, skip=False)
        process_tree = imd.apply(IMDataStructureDFG(idfg), parameters)
    else:
        if type(obj) in [UVCL]:
            uvcl = obj
        else:
            uvcl = comut.get_variants(comut.project_univariate(obj, key=ack, df_glue=cidk, df_sorting_criterion_key=tk))

        if variant is Variants.IM:
            im = IMUVCL(parameters)
            process_tree = im.apply(IMDataStructureUVCL(uvcl), parameters)
        if variant is Variants.IMf:
            imf = IMFUVCL(parameters)
            process_tree = imf.apply(IMDataStructureUVCL(uvcl), parameters)
        if variant is Variants.IMd:
            imd = IMD(parameters)
            idfg = InductiveDFG(dfg=comut.discover_dfg_uvcl(uvcl), skip=() in uvcl)
            process_tree = imd.apply(IMDataStructureDFG(idfg), parameters)

    process_tree = pt_util.fold(process_tree)
    tree_sort(process_tree)

    return process_tree
