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

from pm4py.objects.ocel.obj import OCEL
from typing import Dict, Any, Optional
from pm4py.objects.ocel.util import ocel_consistency
import os


def apply(ocel: OCEL, target_path: str, parameters: Optional[Dict[Any, Any]] = None):
    """
    Exports an OCEL to a SQLite database using Pandas

    Parameters
    ---------------
    ocel
        Object-centric event log
    target_path
        Path to the SQLite database
    parameters
        Parameters of the exporter
    """
    if parameters is None:
        parameters = {}

    import sqlite3

    if os.path.exists(target_path):
        os.remove(target_path)

    ocel = ocel_consistency.apply(ocel, parameters=parameters)

    conn = sqlite3.connect(target_path)

    ocel.events.to_sql("EVENTS", conn, index=False)
    ocel.relations.to_sql("RELATIONS", conn, index=False)
    ocel.objects.to_sql("OBJECTS", conn, index=False)

    conn.close()
