import deprecation


@deprecation.deprecated("2.2.11", "3.0.0", details="removed")
def check_pandas_ge_110():
    """
    Checks if the Pandas version is >= 1.1.0
    """
    import pandas as pd

    MAJOR = int(pd.__version__.split(".")[0])
    INTERM = int(pd.__version__.split(".")[1])

    if (MAJOR == 1 and INTERM >= 1) or MAJOR >= 2:
        return True
    return False


@deprecation.deprecated("2.2.11", "3.0.0", details="removed")
def check_pandas_ge_024():
    """
    Checks if the Pandas version is >= 0.24
    """
    import pandas as pd

    MAJOR = int(pd.__version__.split(".")[0])
    INTERM = int(pd.__version__.split(".")[1])

    if (MAJOR == 0 and INTERM >= 24) or MAJOR >= 1:
        return True

    return False
