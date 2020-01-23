import sys


CISO8601 = "ciso8601"
STRPFROMISO = "strpfromiso"

VERSIONS = {}

try:
    from pm4py.util.dt_parsing.versions import cs8601

    VERSIONS[CISO8601] = cs8601
    DEFAULT_VARIANT = CISO8601
except:
    # ciso8601 is not available
    pass

# this variant is available only for Python 3.7
if sys.version_info >= (3, 7):
    from pm4py.util.dt_parsing.versions import strpfromiso

    VERSIONS[STRPFROMISO] = strpfromiso
    # let's move the default option to strpfromiso in Python 3.7
    # (at least we can drop ciso8601 somewhen)
    DEFAULT_VARIANT = STRPFROMISO


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
