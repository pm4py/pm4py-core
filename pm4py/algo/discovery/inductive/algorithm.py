from enum import Enum
from typing import Optional, Dict, Any, Union, Tuple, Collection

import pandas as pd

from pm4py import util as pmutil
from pm4py.algo.discovery.inductive.dtypes.im_dfg import InductiveDFG
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL, IMDataStructureDFG
from pm4py.algo.discovery.inductive.variants.im import IMUVCL
from pm4py.algo.discovery.inductive.variants.imd import IMD
from pm4py.algo.discovery.inductive.variants.instances import IMInstance
from pm4py.objects.dfg.obj import DFG
from pm4py.objects.log.obj import EventLog
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util import constants
from pm4py.util import exec_utils
from pm4py.util import xes_constants as xes_util
from pm4py.util.compression import util as comut
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.conversion.process_tree import converter


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY


class Variants(Enum):
    IM = IMInstance.IM
    IMf = IMInstance.IMf
    IMd = IMInstance.IMd


def apply(obj: Union[EventLog, pd.DataFrame, DFG], parameters: Optional[Dict[Any, Any]] = None,
          variant=Variants.IM) -> Tuple[PetriNet, Marking, Marking]:
    process_tree = apply_tree(obj, parameters=parameters, variant=variant)
    return converter.apply(process_tree, parameters=parameters)


def apply_tree(obj: Union[EventLog, pd.DataFrame, DFG], parameters: Optional[Dict[Any, Any]] = None,
          variant=Variants.IM) -> ProcessTree:
    if type(obj) not in [EventLog, pd.DataFrame, DFG]:
        raise TypeError('Inductive miner called with an incorrect data type as an input (should be a dataframe or DFG)')
    ack = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_util.DEFAULT_NAME_KEY)
    tk = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_util.DEFAULT_TIMESTAMP_KEY)
    cidk = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, pmutil.constants.CASE_CONCEPT_NAME)
    if type(obj) in [EventLog, pd.DataFrame]:
        uvcl = comut.get_variants(comut.project_univariate(obj, key=ack, df_glue=cidk, df_sorting_criterion_key=tk))
        if variant is Variants.IM:
            im = IMUVCL()
            return im.apply(IMDataStructureUVCL(uvcl))
        if variant is Variants.IMd:
            imd = IMD()
            idfg = InductiveDFG(dfg=comut.discover_dfg_uvcl(uvcl), skip=() in uvcl)
            return imd.apply(IMDataStructureDFG(idfg))
    if type(obj) is DFG:
        if variant is not Variants.IMd:
            raise RuntimeWarning('Inductive Miner Variant requested for DFG artefact is not IMD, resorting back to IMD')
        imd = IMD()
        idfg = InductiveDFG(dfg=obj, skip=False)
        return imd.apply(IMDataStructureDFG(idfg))


def apply_variants(variants: Dict[Collection[str], int], parameters: Optional[Dict[Any, Any]] = None):
    im = IMUVCL()
    return im.apply(IMDataStructureUVCL(variants))
