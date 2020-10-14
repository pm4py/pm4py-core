import pandas as pd


def check_pandas_ge_110():
    """
    Checks if the Pandas version is >= 1.1.0
    """
    MAJOR = int(pd.__version__.split(".")[0])
    INTERM = int(pd.__version__.split(".")[1])

    if (MAJOR == 1 and INTERM >= 1) or MAJOR >= 2:
        return True
    return False


def check_pandas_ge_024():
    """
    Checks if the Pandas version is >= 0.24
    """
    MAJOR = int(pd.__version__.split(".")[0])
    INTERM = int(pd.__version__.split(".")[1])

    if (MAJOR == 0 and INTERM >= 24) or MAJOR >= 1:
        return True

    return False
