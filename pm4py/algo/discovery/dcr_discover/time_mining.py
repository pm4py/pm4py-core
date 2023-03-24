import pm4py
import numpy as np
import pandas as pd
from copy import deepcopy
from enum import Enum


class AggregationMethod(Enum):
    STANDARD = 'standard'
    MEAN = 'mean'
    MEDIAN = 'median'


def apply(dcr_model, event_log, method=AggregationMethod.STANDARD,sp_log=None):
    #TODO: add a parameter for the time according to the desired output.
    # Make sure it's in the ISO format in the DCR (then no need to worry in the export function about it)
    timings = get_timing_values(dcr_model, event_log, sp_log)
    result_dict = {}
    for k, v in timings.items():
        if method == AggregationMethod.MEAN:
            result_dict[k] = np.mean(v)
        elif method == AggregationMethod.MEDIAN:
            result_dict[k] = np.median(v)
        elif len(v) > 0:
            if k[0] == 'RESPONSE':
                # MAX Deadline
                result_dict[k] = np.max(v)
            elif k[0] == 'CONDITION':
                # MIN Delay
                result_dict[k] = np.min(v)
    return result_dict


def get_timing_values(dcr_model, event_log, sp_log):
    timing_input_dict = {}
    timing_input_dict['RESPONSE'] = set()
    timing_input_dict['CONDITION'] = set()
    for e1 in dcr_model['events']:
        for e2 in dcr_model['events']:
            if e1 in dcr_model['responseTo'] and e2 in dcr_model['responseTo'][e1]:
                timing_input_dict['RESPONSE'].add((e1, e2))
            if e1 in dcr_model['conditionsFor'] and e2 in dcr_model['conditionsFor'][e1]:
                timing_input_dict['CONDITION'].add((e2, e1))
    if sp_log:
        return get_timings_subprocess(timing_input_dict, event_log, sp_log, dcr_model['subprocesses'].keys())
    else:
        return get_timings(timing_input_dict, event_log)


def get_delta_between_events(filtered_df, event_pair, rule):
    e1 = event_pair[0]
    e2 = event_pair[1]
    filtered_df = filtered_df[['case:concept:name', 'concept:name', 'time:timestamp']]
    filtered_df = filtered_df[filtered_df['concept:name'].isin(event_pair)]
    filtered_df['time:timestamp'] = pd.to_datetime(filtered_df['time:timestamp'], utc=True)
    deltas = []
    for idx, g in filtered_df[filtered_df['concept:name'].isin([e1, e2])].groupby('case:concept:name'):
        g = g.sort_values(by='time:timestamp').reset_index(drop=True)
        g['time:timestamp:to'] = g['time:timestamp'].shift(-1)
        g['concept:name:to'] = g['concept:name'].shift(-1)
        temp_df = deepcopy(g)
        if rule == 'RESPONSE':
            g_e1 = deepcopy(g[g['concept:name'] == e1])
            if len(g_e1) > 1:
                g_e1 = g_e1.reset_index(drop=False)
                g_e1['index_below'] = g_e1['index'].shift(-1)
                g_e1 = g_e1[((g_e1['index_below'] - g_e1['index']) == 1)]
                g_e1['delta'] = (g_e1['time:timestamp:to'] - g_e1['time:timestamp']).dt.days
                deltas.extend(g_e1['delta'].to_numpy())
            temp_df = temp_df[
                (temp_df['concept:name'] == event_pair[0]) & (temp_df['concept:name:to'] == event_pair[1])]
            temp_df['delta'] = (temp_df['time:timestamp:to'] - temp_df['time:timestamp']).dt.days
            deltas.extend(temp_df['delta'].to_numpy())
        elif rule == 'CONDITION':
            temp_df = temp_df[
                (temp_df['concept:name'] == event_pair[0]) & (temp_df['concept:name:to'] == event_pair[1])]
            temp_df['delta'] = (temp_df['time:timestamp:to'] - temp_df['time:timestamp']).dt.days
            deltas.extend(temp_df['delta'].to_numpy())
    return deltas


def get_log_with_pair(event_log, e1, e2):
    first_e1 = event_log[event_log['concept:name'] == e1].groupby('case:concept:name')[
        ['case:concept:name', 'time:timestamp']].first().reset_index(drop=True)
    subset_is_in = first_e1.merge(event_log, on='case:concept:name', how='inner', suffixes=('_e1', ''))
    cids = subset_is_in[
        ((subset_is_in['time:timestamp_e1'] < subset_is_in['time:timestamp']) & (subset_is_in['concept:name'] == e2))][
        'case:concept:name'].unique()
    return event_log[event_log['case:concept:name'].isin(cids)].copy(deep=True)

def get_timings(timing_input_dict, log):
    if isinstance(log, pd.DataFrame):
        event_log = log
    else:
        event_log = pm4py.convert_to_dataframe(log)
    res = {}
    el_events = event_log['concept:name'].unique()
    for rule, event_pairs in timing_input_dict.items():
        # print(rule)
        for event_pair in event_pairs:
            if event_pair[0] in el_events and event_pair[1] in el_events:
                filtered_df = get_log_with_pair(event_log, event_pair[0], event_pair[1])
                data = get_delta_between_events(filtered_df, event_pair, rule)
                # print(event_pair)
                res[(rule, event_pair[0], event_pair[1])] = data
            # else:
                # print(f'[fuked] {event_pair}')

    return res
def get_timings_subprocess(timing_input_dict, log, sp_log,sps):
    if isinstance(log, pd.DataFrame):
        event_log = log
    else:
        event_log = pm4py.convert_to_dataframe(log)
    # el_events = event_log['concept:name'].unique()

    if isinstance(sp_log, pd.DataFrame):
        sp_event_log = sp_log
    else:
        sp_event_log = pm4py.convert_to_dataframe(sp_log)
    # sp_el_events = sp_event_log['concept:name'].unique()

    res = {}
    for rule, event_pairs in timing_input_dict.items():
        # print(rule)
        for event_pair in event_pairs:
            if event_pair[0] in sps or event_pair[1] in sps:
                filtered_df = get_log_with_pair(sp_event_log, event_pair[0], event_pair[1])
                data = get_delta_between_events(filtered_df, event_pair, rule)
                # print(event_pair)
                res[(rule, event_pair[0], event_pair[1])] = data
            else:
                filtered_df = get_log_with_pair(event_log, event_pair[0], event_pair[1])
                data = get_delta_between_events(filtered_df, event_pair, rule)
                # print(event_pair)
                res[(rule, event_pair[0], event_pair[1])] = data

    return res


def get_timings_subprocess_old(timing_input_dict, log, sp_log):
    if isinstance(log, pd.DataFrame):
        event_log = log
    else:
        event_log = pm4py.convert_to_dataframe(log)
    el_events = event_log['concept:name'].unique()

    if isinstance(sp_log, pd.DataFrame):
        sp_event_log = sp_log
    else:
        sp_event_log = pm4py.convert_to_dataframe(sp_log)
    sp_el_events = sp_event_log['concept:name'].unique()

    res = {}
    for rule, event_pairs in timing_input_dict.items():
        print(rule)
        for event_pair in event_pairs:
            if event_pair[0] in el_events and event_pair[1] in el_events:
                filtered_df = get_log_with_pair(event_log, event_pair[0], event_pair[1])
                data = get_delta_between_events(filtered_df, event_pair, rule)
                print(event_pair)
                res[(rule, event_pair[0], event_pair[1])] = data
            elif event_pair[0] in sp_el_events and event_pair[1] in sp_el_events:
                filtered_df = get_log_with_pair(sp_event_log, event_pair[0], event_pair[1])
                data = get_delta_between_events(filtered_df, event_pair, rule)
                print(event_pair)
                res[(rule, event_pair[0], event_pair[1])] = data
            # elif len(event_pair) >= 2: # in here the in between events end up
            #     print(f'[inbetween] {event_pair}')
            #     filtered_df = get_log_with_pair(event_log, event_pair[0], event_pair[1])
            #     data = get_delta_between_events(filtered_df, event_pair, rule)
            #     print(event_pair)
            #     res[(rule, event_pair[0], event_pair[1])] = data
            else:
                print(f'[fuked_sp] {event_pair}')

    return res