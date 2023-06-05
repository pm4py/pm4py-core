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
from copy import deepcopy

import pm4py.objects.log.obj
from pm4py.algo.discovery.dcr_discover.variants import discover_basic, discover_subprocess_predecessors, \
    discover_subprocess_mutual_exclusion, discover_subprocess_given_domain_knowledge
from pm4py.algo.discovery.dcr_discover import time_mining, initial_pending
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union, Tuple


class Variants(Enum):
    DCR_BASIC = discover_basic
    DCR_SUBPROCESS_PRE = discover_subprocess_predecessors
    DCR_SUBPROCESS_ME = discover_subprocess_mutual_exclusion
    DCR_SUBPROCESS_DK = discover_subprocess_given_domain_knowledge


DCR_BASIC = Variants.DCR_BASIC
DCR_SUBPROCESS_PRE = Variants.DCR_SUBPROCESS_PRE
DCR_SUBPROCESS_ME = Variants.DCR_SUBPROCESS_ME
DCR_SUBPROCESS_DK = Variants.DCR_SUBPROCESS_DK

VERSIONS = {DCR_BASIC, DCR_SUBPROCESS_PRE, DCR_SUBPROCESS_ME, DCR_SUBPROCESS_DK}


def apply(input_log, variant=DCR_BASIC, **parameters):
    """
    Parameters
    -----------
    input_log
    variant
        Variant of the algorithm to use:
            - DCR_BASIC
            - DCR_SUBPROCESS_ME
    parameters
        Algorithm related params
        finaAdditionalConditions: [True or False]
    Returns
    -----------
    dcr graph
    """
    log = deepcopy(input_log)
    if variant.value == Variants.DCR_BASIC.value:
        print('[i] Mining with basic DisCoveR')
        if not isinstance(log, pm4py.objects.log.obj.EventLog):
            log = pm4py.convert_to_event_log(log)
        disc_b = discover_basic.Discover()
        dcr_model, la = disc_b.mine(log, **parameters)
        if 'timed' in parameters.keys() and parameters['timed']:
            dcr_model = apply_timed(dcr_model, log, None)
        if 'pending' in parameters.keys() and parameters['pending']:
            dcr_model = initial_pending.apply(dcr_model, log)
        return dcr_model, la
    elif variant.value == Variants.DCR_SUBPROCESS_ME.value:
        print('[i] Mining with Sp-DisCoveR (ME)')
        dcr_model, sp_log = discover_subprocess_mutual_exclusion.apply(log, **parameters)
        if 'timed' in parameters.keys() and parameters['timed']:
            dcr_model = apply_timed(dcr_model, deepcopy(input_log), sp_log)
        if 'pending' in parameters.keys() and parameters['pending']:
            dcr_model = initial_pending.apply(dcr_model, sp_log)
        return dcr_model, sp_log
    elif variant.value == Variants.DCR_SUBPROCESS_DK.value:
        print('[i] Mining with Sp-DisCoveR (DK)')
        dcr_model, sp_log = discover_subprocess_given_domain_knowledge.apply(log, **parameters)
        if 'timed' in parameters.keys() and parameters['timed']:
            dcr_model = apply_timed(dcr_model, deepcopy(input_log), sp_log)
        if 'pending' in parameters.keys() and parameters['pending']:
            dcr_model = initial_pending.apply(dcr_model, sp_log)
        return dcr_model, sp_log
    elif variant.value == Variants.DCR_SUBPROCESS_PRE.value:
        dcr_model, sp_log = discover_subprocess_predecessors.apply(log, **parameters)
        if 'timed' in parameters.keys() and parameters['timed']:
            dcr_model = apply_timed(dcr_model, deepcopy(input_log), sp_log)
        if 'pending' in parameters.keys() and parameters['pending']:
            dcr_model = initial_pending.apply(dcr_model, sp_log)
        return dcr_model, sp_log


def apply_timed(dcr_model, log, sp_log):
    timings = time_mining.apply(dcr_model=dcr_model, event_log=log, method='standard', sp_log=sp_log)
    # these should be a dict with events as keys and tuples as values
    if 'conditionsForDelays' not in dcr_model:
        dcr_model['conditionsForDelays'] = {}
    if 'responseToDeadlines' not in dcr_model:
        dcr_model['responseToDeadlines'] = {}
    for timing, value in timings.items():
        if timing[0] == 'CONDITION':
            e1 = timing[2]
            e2 = timing[1]
            if e1 not in dcr_model['conditionsForDelays']:
                dcr_model['conditionsForDelays'][e1] = {}
            dcr_model['conditionsForDelays'][e1][e2] = value
        elif timing[0] == 'RESPONSE':
            e1 = timing[1]
            e2 = timing[2]
            if e1 not in dcr_model['responseToDeadlines']:
                dcr_model['responseToDeadlines'][e1] = {}
            dcr_model['responseToDeadlines'][e1][e2] = value
    return dcr_model
