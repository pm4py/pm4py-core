'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''

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
