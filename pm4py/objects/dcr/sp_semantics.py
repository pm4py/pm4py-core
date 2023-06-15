from copy import deepcopy
import semantics as sem

rels = ['conditionsFor', 'responseTo', 'includesTo', 'excludesTo']


def get_atomic_sp_and_top_level_events(dcr):
    all_events = set(dcr['events'])
    if 'subprocesses' in dcr.keys():
        sp_events = set(dcr['subprocesses'].keys())
        atomic_events = all_events.difference(sp_events)
        in_sp_events = set()
        for k, v in dcr['subprocesses'].items():
            in_sp_events = in_sp_events.union(v)
        tl_events = all_events.difference(in_sp_events)
        return atomic_events, sp_events, tl_events
    else:
        return all_events, set(), all_events


def get_ancestors(dcr, e, top_level_events, ancestors=None):
    # first loop set it to an empty set
    if ancestors is None:
        ancestors = set()
    # for each subprocess
    if 'subprocesses' in dcr.keys():
        for k, v in dcr['subprocesses'].items():
            if e in v:
                # if the event is in the subprocess add that key as its ancestor
                ancestors.add(k)
                # if the key is a top level event we are done
                if k in top_level_events:
                    break
                else:
                    # if the event is not a top level event then we go into the key of that subprocess and repeat
                    ancestors = ancestors.union(get_ancestors(dcr, k, ancestors))
    return ancestors


def find_all_ancestors(dcr, tl_e):
    ancestors_dict = {}
    # for each event find the ancestors
    for e in dcr['events']:
        ancestors_dict[e] = get_ancestors(dcr, e, tl_e)
    return ancestors_dict


def is_effectively_included(dcr, e, ancestors_dict):
    return ancestors_dict[e].issubset(dcr['marking']['included'])


def get_effectively_pending(dcr, e, ancestors_dict):
    return ancestors_dict[e].issubset(dcr['marking']['pending'])


def is_enabled(e, dcr):
    at_e, sp_e, tl_e = get_atomic_sp_and_top_level_events(dcr)
    e_enabled = sem.is_enabled(e, dcr)
    if e_enabled is True:
        es_ancestors = get_ancestors(dcr, e, tl_e)
        for anc in es_ancestors:
            e_enabled = e_enabled and sem.is_enabled(anc, dcr)

    return e_enabled


def is_accepting(dcr):
    at_e, sp_e, tl_e = get_atomic_sp_and_top_level_events(dcr)
    pend_incl = dcr['marking']['pending'].intersection(dcr['marking']['included'])
    tle_pend_incl = pend_incl.intersection(tl_e)
    return len(tle_pend_incl) == 0


def execute(e, dcr, cmd_print=False):
    at_e, sp_e, tl_e = get_atomic_sp_and_top_level_events(dcr)
    if e in dcr['events']:
        if sem.is_enabled(e, dcr):
            sem.weak_execute(e, dcr)
            ancs = get_ancestors(dcr, e, tl_e)
            for anc in ancs:
                if sem.is_enabled(anc, dcr):
                    sem.weak_execute(anc, dcr)
                else:
                    return False
            return True
        else:
            print(f'[!] Event {e} not enabled!') if cmd_print else None
            return False
    else:
        print(f'[!] Event {e} does not exist!') if cmd_print else None
        return False


# def enabled(dcr):
#     res = deepcopy(dcr['marking']['included'])
#     for e in dcr['conditionsFor']:
#         if e in res:
#             for e_prime in dcr['conditionsFor'][e]:
#                 if e_prime in dcr['marking']['included'] and e_prime not in dcr['marking']['executed']:
#                     res.discard(e)
#     return res
#
#
# def is_enabled(e, dcr):
#     return e in enabled(dcr)
#
# def is_accepting(dcr):
#     pend_incl = dcr['marking']['pending'].intersection(dcr['marking']['included'])
#     return len(pend_incl) == 0
#
# def execute(e, dcr, cmd_print=False):
#     if e in dcr['events']:
#         if is_enabled(e, dcr):
#             weak_execute(e, dcr)
#             return True
#         else:
#             print(f'[!] Event {e} not enabled!') if cmd_print else None
#             return False
#     else:
#         print(f'[!] Event {e} does not exist!') if cmd_print else None
#         return False
#
#
# def weak_execute(e, dcr):
#     '''
#     Executes events even if not enabled. This will break the condition constraint.
#     :param e:
#     :param dcr:
#     :return:
#     '''
#     dcr['marking']['pending'].discard(e)
#     dcr['marking']['executed'].add(e)
#     if e in dcr['excludesTo']:
#         for e_prime in dcr['excludesTo'][e]:
#             dcr['marking']['included'].discard(e_prime)
#     if e in dcr['includesTo']:
#         for e_prime in dcr['includesTo'][e]:
#             dcr['marking']['included'].add(e_prime)
#     if e in dcr['responseTo']:
#         for e_prime in dcr['responseTo'][e]:
#             dcr['marking']['pending'].add(e_prime)
