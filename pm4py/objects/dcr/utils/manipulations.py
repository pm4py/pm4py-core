from pm4py.objects.dcr.obj import Relations

def flatten_dcr_hierarchies(dcr):
    '''
    Given a dcr graph with nestings and/or subprocesses or any other general grouping
    it moves all relations to the top level events (atomic events, the ones that exist without and other events in them)
    Parameters
    ----------
    dcr: the dcr you want to flatten
    Returns: the flat dcr with no nestings
    -------
    '''
    for groups in ['nestings', 'subprocesses']:
        for nesting_event, events_nested in dcr[groups].items():
            for rel in Relations:
                if nesting_event in dcr[rel.value].keys():
                    other_events = dcr[rel.value].pop(nesting_event, set())
                    for event_nested in events_nested:
                        dcr[rel.value][event_nested] = other_events
                for k, v in dcr[rel.value].items():
                    if nesting_event in v:
                        v.remove(nesting_event)
                        v = v.union(events_nested)
    return dcr