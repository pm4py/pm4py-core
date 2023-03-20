import os
import sqlite3
from datetime import datetime
import pandas as pd
from enum import Enum
from typing import Optional, Dict, Any
from pm4py.util import exec_utils


class Parameters(Enum):
    HISTORY_DB_PATH = "history_db_path"


def apply(parameters: Optional[Dict[Any, str]] = None) -> pd.DataFrame:
    """
    Extracts a dataframe containing the navigation history of Mozilla Firefox.
    Please keep Google Mozilla Firefox closed when extracting.

    CASE ID (case:concept:name) => an identifier of the profile that has been extracted
    ACTIVITY (concept:name) => the complete path of the website, minus the GET arguments
    TIMESTAMP (time:timestamp) => the timestamp of visit

    Parameters
    --------------
    Parameters.HISTORY_DB_PATH
        Path to the history DB path of Mozilla Firefox (default: position of the Windows folder)

    Returns
    --------------
    dataframe
        Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    history_db_path = exec_utils.get_param_value(Parameters.HISTORY_DB_PATH, parameters, "C:\\Users\\" + os.getenv(
        'USERNAME') + "\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles")
    print(history_db_path)

    if os.path.isdir(history_db_path):
        profiles = [(os.path.join(history_db_path, x, "places.sqlite"), x) for x in os.listdir(history_db_path)]
    else:
        profiles = [(history_db_path, "DEFAULT")]

    profiles = [x for x in profiles if os.path.exists(x[0])]

    events = []
    for prof in profiles:
        if os.path.exists(prof[0]):
            conn = sqlite3.connect(prof[0])
            curs = conn.cursor()
            curs.execute(
                "SELECT b.url, a.visit_date FROM (SELECT id, visit_date FROM moz_historyvisits) a JOIN (SELECT id, url FROM moz_places) b ON a.id = b.id")
            res = curs.fetchall()
            for r in res:
                ev = {"case:concept:name": prof[1], "concept:name": r[0].split("//")[-1].split("?")[0].replace(",", ""), "complete_url": r[0],
                  "domain": r[0].split("//")[-1].split("/")[0], "url_wo_parameters": r[0].split("//")[-1].split("?")[0],
                  "time:timestamp": datetime.fromtimestamp(r[1]/10**6)}
                if len(ev["case:concept:name"].strip()) > 0 and len(ev["concept:name"].strip()) > 0:
                    events.append(ev)
            curs.close()
            conn.close()

    dataframe = pd.DataFrame(events)
    if len(dataframe) > 0:
        dataframe["@@index"] = dataframe.index
        dataframe = dataframe.sort_values(["time:timestamp", "@@index"])
        dataframe["@@case_index"] = dataframe.groupby("case:concept:name", sort=False).ngroup()
        dataframe = dataframe.sort_values(["@@case_index", "time:timestamp", "@@index"])
    return dataframe
