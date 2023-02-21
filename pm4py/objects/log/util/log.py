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
from pm4py.util import xes_constants as xes_util


# TODO: we can do some instance checking and then support both trace level and event level logs..
def get_event_labels(event_log, key):
    """
    Fetches the labels present in a log, given a key to use within the events.

    Parameters
    ----------
    :param event_log: log to use
    :param key: to use for event identification, can for example  be "concept:name"

    Returns
    -------
    :return: a list of labels
    """
    labels = []
    for t in event_log:
        for e in t:
            if key in e and e[key] not in labels:
                labels.append(e[key])
    return labels


def get_event_labels_counted(event_log, key):
    """
    Fetches the labels (and their frequency) present in a log, given a key to use within the events.

    Parameters
    ----------
    :param event_log: log to use
    :param key: to use for event identification, can for example  be "concept:name"

    Returns
    -------
    :return: a list of labels
    """
    labels = dict()
    for t in event_log:
        for e in t:
            if key in e:
                if e[key] not in labels:
                    labels[e[key]] = 0
                labels[e[key]] = labels[e[key]] + 1
    return labels


def get_trace_variants(event_log, key=xes_util.DEFAULT_NAME_KEY):
    """
    Returns a pair of a list of (variants, dict[index -> trace]) where the index of a variant maps to all traces
    describing that variant, with that key.

    Parameters
    ---------
    :param event_log: log
    :param key: key to use to identify the label of an event

    Returns
    -------
    :return:
    """
    variants = []
    variant_map = dict()
    for t in event_log:
        variant = list(map(lambda e: e[key], t))
        new = True
        for i in range(0, len(variants)):
            if variants[i] == variant:
                variant_map[i].append(t)
                new = False
                break
        if new:
            variant_map[len(variants)] = [t]
            variants.append(variant)
    return variants, variant_map


def project_traces(event_log, keys=xes_util.DEFAULT_NAME_KEY):
    """
    projects traces on a (set of) event attribute key(s).
    If the key provided is of type string, each trace is converted into a list of strings.
    If the key provided is a collection, each trace is converted into a list of (smaller) dicts of key value pairs

    :param event_log:
    :param keys:
    :return:
    """
    if isinstance(keys, str):
        return list(map(lambda t: list(map(lambda e: e[keys], t)), event_log))
    else:
        return list(map(lambda t: list(map(lambda e: {key: e[key] for key in keys}, t)), event_log))


def derive_and_lift_trace_attributes_from_event_attributes(trlog, ignore=None, retain_on_event_level=False,
                                                           verbose=False):
    if ignore is None:
        ignore = set()
    candidates = set(trlog[0][0].keys())
    for i in ignore:
        candidates.remove(i)
    if verbose:
        print('candidates: %s' % candidates)
    for t in trlog:
        attr = dict(t[0])
        for e in t:
            for k in candidates.copy():
                if k not in e:
                    if verbose:
                        print('removing %s, was not present in event' % k)
                    candidates.remove(k)
                    continue
                if e[k] != attr[k]:
                    if verbose:
                        print('removing ' + k + ' for trace with id ' + t.attributes[
                            'concept:name'] + ', mismatch ' + str(e[k]) + ' != ' + str(attr[k]))
                    candidates.remove(k)
                    continue
            if len(candidates) == 0:
                return trlog

    for t in trlog:
        for key in candidates:
            t.attributes[key] = t[0][key]
            if not retain_on_event_level:
                for e in t:
                    del e[key]

    return trlog


def add_artficial_start_and_end(event_log, start='[start>', end='[end]', activity_key=xes_util.DEFAULT_NAME_KEY):
    for trace in event_log:
        trace.insert(0, event_log.Event({activity_key: start}))
        trace.append(event_log.Event({activity_key: end}))
    return event_log

