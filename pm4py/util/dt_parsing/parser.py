import sys
import pkgutil
import warnings
from pm4py.util import constants


CISO8601 = "ciso8601"
STRPFROMISO = "strpfromiso"
DUMMY = "dummy"

VERSIONS = {}


from pm4py.util.dt_parsing.variants import dummy
VERSIONS[DUMMY] = dummy
# this option should never be used, except in particular situations
# (problematic Python <= 3.4,3.5,3.6 environments)
DEFAULT_VARIANT = DUMMY


# this variant is available only for Python 3.7 and greater
if sys.version_info >= (3, 7):
    from pm4py.util.dt_parsing.variants import strpfromiso

    VERSIONS[STRPFROMISO] = strpfromiso

    DEFAULT_VARIANT = STRPFROMISO

if pkgutil.find_loader("ciso8601"):
    # ciso8601 variant is included only if ciso8601 installed
    # slowly it will fade out of the default since now Python
    # in the default package includes an equally performing library
    #
    # ciso8601 will be installed from requirements only if the Python
    # version is <= than 3.6
    from pm4py.util.dt_parsing.variants import cs8601

    VERSIONS[CISO8601] = cs8601
    DEFAULT_VARIANT = CISO8601


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
    if DEFAULT_VARIANT == STRPFROMISO:
        if not constants.TRIGGERED_DT_PARSING_WARNING:
            if sys.version_info < (3, 11):
                warnings.warn(
                    "ISO8601 strings are not fully supported with strpfromiso for Python versions below 3.11")
                constants.TRIGGERED_DT_PARSING_WARNING = True

    return VERSIONS[variant]
