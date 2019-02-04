import pandas as pd


def check_pandas_ge_024():
    """
    Checks if the Pandas version is >= 0.24
    :return:
    """
    MAJOR = int(pd.__version__.split(".")[0])
    INTERM = int(pd.__version__.split(".")[1])

    if MAJOR >= 0 and INTERM >= 24:
        return True

    return False
