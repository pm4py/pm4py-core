from copy import deepcopy

rels = ['conditionsFor', 'responseTo', 'includesTo', 'excludesTo']


def enabled(dcr):
    res = deepcopy(dcr['marking']['included'])
    for e in dcr['conditionsFor']:
        if e in res:
            for e_prime in dcr['conditionsFor'][e]:
                if e_prime in dcr['marking']['included'] and e_prime not in dcr['marking']['executed']:
                    res.discard(e)
    return res


def is_enabled(e, dcr):
    return e in enabled(dcr)


def execute(e, dcr):
    if e in dcr['events']:
        if is_enabled(e, dcr):
            weak_execute(e, dcr)
        else:
            print(f'[!] Event {e} not enabled!')
    else:
        print(f'[!] Event {e} does not exist!')


def weak_execute(e, dcr):
    '''
    Executes events even if not enabled. This will break the condition constraint.
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


def is_accepting(dcr):
    pend_incl = dcr['marking']['pending'].intersection(dcr['marking']['included'])
    return len(pend_incl) == 0
