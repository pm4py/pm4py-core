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
from datetime import datetime, timezone
from pm4py.util import constants


def fix_dataframe_column(serie):
    if constants.ENABLE_DATETIME_COLUMNS_AWARE:
        # Convert to UTC if the datetime is naive
        if serie.dt.tz is None:
            serie = serie.dt.tz_localize('UTC')
        else:
            # Convert to UTC if it's not already in UTC
            serie = serie.dt.tz_convert('UTC')
    else:
        serie = serie.dt.tz_localize(None)

    return serie


def fix_naivety(dt):
    if constants.ENABLE_DATETIME_COLUMNS_AWARE:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.replace(tzinfo=None)

    return dt


def apply(dt):
    """
    Parses the string to a datetime object (uses Python default strptime)

    Parameters
    --------------
    dt
        Date string

    Returns
    --------------
    datetime
        Datetime object
    """
    if dt.endswith("Z"):
        # Z at the end of date means UTC, but that is not ISO format.
        # Replace "Z" with "+00:00" that is also UTC
        dt = dt[:-1] + "+00:00"
    dt = datetime.fromisoformat(dt)

    return fix_naivety(dt)
