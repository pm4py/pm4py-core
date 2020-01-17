from pm4py.util.dt_parsing.versions import cs8601, strpfromiso

CISO8601 = "ciso8601"
STRPFROMISO = "strpfromiso"

DEFAULT_VARIANT = CISO8601

VERSIONS = {CISO8601: cs8601, STRPFROMISO: strpfromiso}


def get(variant=DEFAULT_VARIANT):
    """
    Gets a module with a function 'apply' that is
    able to parse a date string to a datetime

    Parameters
    --------------
    variant
        Variant of the algorithm. Possible values: ciso8601

    Returns
    -------------
    mod
        Module with a function 'apply' that is able to parse a date string to a datetime
    """
    return VERSIONS[variant]
