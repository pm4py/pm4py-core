def fetch(p, params):
    '''
    Assumes a given parameter p (enum) and a collection of (enum) -> value mappings.
    If the param exists, it is returned, if not, the default value is given.

    Parameters
    ----------
    p
    params

    Returns
    -------

    '''
    return params[p] if p in params else p.value
