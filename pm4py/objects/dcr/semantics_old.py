from copy import deepcopy

rels = ['conditionsFor', 'responseTo', 'includesTo', 'excludesTo']

#TODO: add subprocess and timed execution semantics


def execute(e, dcr, cmd_print=False):
    if e in dcr['events']:
        if is_enabled(e, dcr):
            weak_execute(e, dcr)
            return True
        else:
            print(f'[!] Event {e} not enabled!') if cmd_print else None
            return False
    else:
        # TODO: make time pass x duration
        print(f'[!] Event {e} does not exist!') if cmd_print else None
        return False


def is_accepting(dcr):
    pend_incl = dcr['marking']['pending'].intersection(dcr['marking']['included'])
    return len(pend_incl) == 0


def is_enabled(e, dcr):
    return e in enabled(dcr)
def enabled(dcr):
    res = deepcopy(dcr['marking']['included'])
    for e in dcr['conditionsFor']:
        if e in res:
            for e_prime in dcr['conditionsFor'][e]:
                if e_prime in dcr['marking']['included'] and e_prime not in dcr['marking']['executed']:
                    res.discard(e)
    # TODO: extend with milestones
    return res

def weak_execute(e, dcr):
    '''
    Executes events even if not enabled. This will break the condition (TODO: in the future the milestone) constraint.
    :param e:
    :param dcr:
    :return:
    '''
    dcr['marking']['pending'].discard(e)
    dcr['marking']['executed'].add(e)
    if e in dcr['excludesTo']:
        for e_prime in dcr['excludesTo'][e]:
            dcr['marking']['included'].discard(e_prime)
    if e in dcr['includesTo']:
        for e_prime in dcr['includesTo'][e]:
            dcr['marking']['included'].add(e_prime)
    if e in dcr['responseTo']:
        for e_prime in dcr['responseTo'][e]:
            dcr['marking']['pending'].add(e_prime)
    # TODO: extend with milestones


