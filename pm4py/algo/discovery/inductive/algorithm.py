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

from pm4py.algo.discovery.inductive.variants.im import algorithm as im_algo
from pm4py.algo.discovery.inductive.variants.im_clean import algorithm as im_clean
from pm4py.algo.discovery.inductive.variants.im_d import dfg_based
from pm4py.algo.discovery.inductive.variants.im_f import algorithm as im_f_algo
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union, Tuple, List
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.process_tree.obj import ProcessTree


class Variants(Enum):
    IMd = dfg_based
    IM = im_algo
    IMf = im_f_algo
    IM_CLEAN = im_clean


IM = Variants.IM
IMf = Variants.IMf
IMd = Variants.IMd
IM_CLEAN = Variants.IM_CLEAN

VERSIONS = {Variants.IMd, Variants.IM, Variants.IMf, Variants.IM_CLEAN}

DEFAULT_VARIANT_LOG = IM_CLEAN
DEFAULT_VARIANT_VARIANTS = IM_CLEAN
DEFAULT_VARIANT_DFG = IMd


def apply(log: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None, variant=DEFAULT_VARIANT_LOG) -> Tuple[PetriNet, Marking, Marking]:
    """
    Apply the chosen IM algorithm to a log obtaining a Petri net along with an initial and final marking

    Parameters
    -------------
    log
        Log
    variant
        Variant of the algorithm to apply, possible values:
        - Variants.IMd
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)

    Returns
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    return exec_utils.get_variant(variant).apply(log, parameters=parameters)


def apply_dfg(dfg: Dict[Tuple[str, str], int], parameters=None, variant=DEFAULT_VARIANT_DFG) -> Tuple[PetriNet, Marking, Marking]:
    """
    Apply the chosen IM algorithm to a DFG graph obtaining a Petri net along with an initial and final marking

    Parameters
    -----------
    dfg
        Directly-Follows graph
    variant
        Variant of the algorithm to apply, possible values:
        - Variants.IMd
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)

    Returns
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    return exec_utils.get_variant(variant).apply_dfg(dfg, parameters=parameters)


def apply_tree(log: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None, variant=DEFAULT_VARIANT_LOG) -> ProcessTree:
    """
    Apply the chosen IM algorithm to a log obtaining a process tree

    Parameters
    ----------
    log
        Log
    variant
        Variant of the algorithm to apply, possible values:
        - Variants.IMd
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)

    Returns
    ----------
    tree
        Process tree
    """
    return exec_utils.get_variant(variant).apply_tree(log, parameters=parameters)


def apply_tree_dfg(dfg: Dict[Tuple[str, str], int], parameters: Optional[Dict[Any, Any]] = None, variant=DEFAULT_VARIANT_DFG) -> ProcessTree:
    """
    Apply the chosen IM algorithm to a DFG graph obtaining a process tree

    Parameters
    ----------
    dfg
        Directly-follows graph
    variant
        Variant of the algorithm to apply, possible values:
        - Variants.IMd
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)

    Returns
    ----------
    tree
        Process tree
    """
    return exec_utils.get_variant(variant).apply_tree_dfg(dfg, parameters=parameters)


def apply_variants(variants: Dict[Union[str, List[str]], int], parameters: Optional[Dict[Any, Any]] = None, variant=DEFAULT_VARIANT_VARIANTS) -> Tuple[PetriNet, Marking, Marking]:
    """
    Apply the chosen IM algorithm to a dictionary/list/set of variants obtaining a Petri net along with an initial and final marking

    Parameters
    -----------
    variants
        Dictionary/list/set of variants in the log
    variant
        Variant of the algorithm to apply, possible values:
        - Variants.IMd
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)

    Returns
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    return exec_utils.get_variant(variant).apply_variants(variants, parameters=parameters)


def apply_tree_variants(variants: Dict[Union[str, List[str]], int], parameters: Optional[Dict[Any, Any]] = None, variant=DEFAULT_VARIANT_VARIANTS) -> ProcessTree:
    """
    Apply the chosen IM algorithm to a dictionary/list/set of variants a log obtaining a process tree

    Parameters
    ----------
    variants
        Dictionary/list/set of variants in the log
    variant
        Variant of the algorithm to apply, possible values:
        - Variants.IMd
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> attribute of the log to use as activity name (default concept:name)

    Returns
    ----------
    tree
        Process tree
    """
    return exec_utils.get_variant(variant).apply_tree_variants(variants, parameters=parameters)
