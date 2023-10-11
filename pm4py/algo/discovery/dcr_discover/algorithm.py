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
import datetime
from copy import deepcopy

import pm4py.objects.log.obj
from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
from pm4py.algo.discovery.dcr_discover.extenstions import time_constraints, initial_pending, subprocess
from enum import Enum


class Variants(Enum):
    DCR_BASIC = dcr_discover
    DCR_SUBPROCESS = subprocess


DCR_BASIC = Variants.DCR_BASIC
DCR_SUBPROCESS = Variants.DCR_SUBPROCESS

VERSIONS = {DCR_BASIC, DCR_SUBPROCESS}


def apply(input_log, variant=DCR_BASIC, **parameters):
    """
    Parameters
    -----------
    input_log
    variant
        Variant of the algorithm to use:
            - DCR_BASIC
            - DCR_SUBPROCESS
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
            print('[i] Converting to old event log!')
            log = pm4py.convert_to_event_log(log)
        disc_b = dcr_discover.Discover()
        dcr_model, la = disc_b.mine(log, **parameters)
        if 'timed' in parameters.keys() and parameters['timed']:
            dcr_model = apply_timed(dcr_model, log, None)
        if 'pending' in parameters.keys() and parameters['pending']:
            dcr_model = initial_pending.apply(dcr_model, log)
        return dcr_model, la
    elif variant.value == Variants.DCR_SUBPROCESS.value:
        print('[i] Mining with Sp-DisCoveR')
        dcr_model, sp_log = subprocess.apply(log, **parameters)
        if 'timed' in parameters.keys() and parameters['timed']:
            dcr_model = apply_timed(dcr_model, deepcopy(input_log), sp_log)
        if 'pending' in parameters.keys() and parameters['pending']:
            dcr_model = initial_pending.apply(dcr_model, sp_log)
        dcr_model = post_processing(dcr_model, **parameters)
        return dcr_model, sp_log


def post_processing(dcr, timed=True, nestings=False,  **parameters):
    if timed:
        dcr = post_processing_timed(dcr)
    # future work on nestings
    # if nestings:
        # dcr = post_processing_nestings(dcr)
    return dcr


def post_processing_timed(dcr):
    # if there is a timed condition wrap it in a subprocess to still enforce the time
    # we do this due to the way we mine time from the event log which is different from the definition of a
    # delay condition. This delay is observed in all log traces therefore it is more accurate w.r.t. the log
    # to have this delay persist event after the executed event is excluded
    conditions = deepcopy(dcr['conditionsForDelays'])
    for e1, cond_time_dict in conditions.items():
        for e0, time in cond_time_dict.items():
            if time > datetime.timedelta(0):
                new_sp = f'{e0}_ne'  # not excluded
                dcr = replace_events_ne(dcr, e0, new_sp)
                dcr['subprocesses'][new_sp] = set([e0])
    # if there are 2 or more events that have the exact same relations to/from the exact same events
    # then they can be grouped into subprocesses. This can be done iteratively. Discover a subprocess then
    # group that subprocess based on the same rule.
    return dcr


def replace_events_ne(dcr, e0, new_sp):
    new_dcr = deepcopy(dcr)
    new_dcr['events'].add(new_sp)
    for m in ['executed', 'included', 'pending']:
        if e0 in dcr['marking'][m]:
            new_dcr['marking'][m].add(new_sp)
    for k, v in dcr['conditionsFor'].items():
        if e0 in v:
            new_dcr['conditionsFor'][k].discard(e0)
            new_dcr['conditionsFor'][k].add(new_sp)
    for k, v in dcr['conditionsForDelays'].items():
        if e0 in v.keys():
            new_dcr['conditionsForDelays'][k][new_sp] = new_dcr['conditionsForDelays'][k].pop(e0)
    return new_dcr


def apply_timed(dcr_model, log, sp_log):
    timings = time_constraints.apply(dcr_model=dcr_model, event_log=log, method='standard', sp_log=sp_log)
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
