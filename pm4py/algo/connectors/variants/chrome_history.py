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

import os
import sqlite3
from datetime import datetime
import pandas as pd
from enum import Enum
from typing import Optional, Dict, Any
from pm4py.util import exec_utils, pandas_utils


class Parameters(Enum):
    HISTORY_DB_PATH = "history_db_path"


def apply(parameters: Optional[Dict[Any, str]] = None) -> pd.DataFrame:
    """
    Extracts a dataframe containing the navigation history of Google Chrome.
    Please keep Google Chrome history closed when extracting.

    CASE ID (case:concept:name) => an identifier of the profile that has been extracted
    ACTIVITY (concept:name) => the complete path of the website, minus the GET arguments
    TIMESTAMP (time:timestamp) => the timestamp of visit

    Parameters
    --------------
    Parameters.HISTORY_DB_PATH
        Path to the history DB path of Google Chrome (default: position of the Windows folder)

    Returns
    --------------
    dataframe
        Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    history_db_path = exec_utils.get_param_value(Parameters.HISTORY_DB_PATH, parameters, "C:\\Users\\" + os.getenv(
        'USERNAME') + "\\AppData\\Local\\Google\\Chrome\\User Data")
    print(history_db_path)

    if os.path.isdir(history_db_path):
        profiles = [(os.path.join(history_db_path, x, "History"), x) for x in os.listdir(history_db_path) if
                    x.startswith("Profile ")]
    else:
        profiles = [(history_db_path, "DEFAULT")]

    profiles = [x for x in profiles if os.path.exists(x[0])]

    events = []
    for prof in profiles:
        conn = sqlite3.connect(prof[0])
        curs = conn.cursor()
        curs.execute(
            "SELECT b.url, datetime(a.visit_time / 1000000 + (strftime('%s', '1601-01-01')), 'unixepoch', 'localtime') FROM (SELECT url, visit_time FROM visits) a JOIN (SELECT id, url FROM urls) b ON a.url = b.id")
        res = curs.fetchall()
        for r in res:
            ev = {"case:concept:name": prof[1], "concept:name": r[0].split("//")[-1].split("?")[0].replace(",", ""),
                  "complete_url": r[0],
                  "domain": r[0].split("//")[-1].split("/")[0], "url_wo_parameters": r[0].split("//")[-1].split("?")[0],
                  "time:timestamp": datetime.strptime(r[1], "%Y-%m-%d %H:%M:%S")}
            if len(ev["case:concept:name"].strip()) > 0 and len(ev["concept:name"].strip()) > 0:
                events.append(ev)
        curs.close()
        conn.close()

    dataframe = pandas_utils.instantiate_dataframe(events)
    if len(dataframe) > 0:
        dataframe = pandas_utils.insert_index(dataframe, "@@index", copy_dataframe=False, reset_index=False)
        dataframe = dataframe.sort_values(["time:timestamp", "@@index"])
        dataframe["@@case_index"] = dataframe.groupby("case:concept:name", sort=False).ngroup()
        dataframe = dataframe.sort_values(["@@case_index", "time:timestamp", "@@index"])
    return dataframe
