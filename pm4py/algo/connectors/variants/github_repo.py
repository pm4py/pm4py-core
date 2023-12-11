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

import time
import traceback
import pandas as pd
from dateutil.parser import parse
from pm4py.util.dt_parsing.variants import strpfromiso
from typing import Optional, Dict, Any
from enum import Enum
from pm4py.util import exec_utils, pandas_utils
import importlib.util


class Parameters(Enum):
    OWNER = "owner"
    REPOSITORY = "repository"
    AUTH_TOKEN = "auth_token"


def apply(parameters: Optional[Dict[Any, str]] = None) -> pd.DataFrame:
    """
    Extracts a dataframe containing the history of the issues of a Github repository.
    According to the API limit rate of public/registered users, only a part of the events
    can be returned.

    Parameters
    ---------------
    prameters
        Parameters of the algorithm, including:
        - Parameters.OWNER => owner of the repository (e.g., pm4py)
        - Parameters.REPOSITORY => name of the repository (e.g., pm4py-core)
        - Parameters.AUTH_TOKEN => authorization token

    Returns
    ---------------
    dataframe
        Pandas dataframe
    """
    import requests

    if parameters is None:
        parameters = {}

    owner = exec_utils.get_param_value(Parameters.OWNER, parameters, "pm4py")
    repo = exec_utils.get_param_value(Parameters.REPOSITORY, parameters, "pm4py-core")
    auth_token = exec_utils.get_param_value(Parameters.AUTH_TOKEN, parameters, None)

    headers = {}
    if auth_token is not None:
        headers["Authorization"] = "Bearer "+auth_token

    continuee = True
    page = 0
    events = []

    progress = None

    while continuee:
        page += 1
        try:
            r = requests.get("https://api.github.com/repos/"+owner+"/"+repo+"/issues?state=all&per_page=100&page="+str(page), headers=headers)
            issues = r.json()
            if not issues:
                continuee = False
                break

            if importlib.util.find_spec("tqdm"):
                from tqdm.auto import tqdm
                progress = tqdm(total=len(issues),
                                desc="extracting issues of page " + str(page) + ", progress :: ")

            for i in issues:
                if continuee:
                    if "timeline_url" in i:
                        timeline_url = i["timeline_url"]
                        eve = {"case:owner": owner, "case:repo": owner+"/"+repo, "case:concept:name": timeline_url, "time:timestamp": strpfromiso.fix_naivety(parse(i["created_at"])), "concept:name": "created", "org:resource": i["user"]["login"], "case:author_association": i["author_association"], "case:title": i["title"]}
                        if "pull_request" in i:
                            eve["case:pull_request"] = i["pull_request"]["url"]
                        events.append(eve)
                        r2 = requests.get(timeline_url, headers=headers)
                        issue_events = r2.json()
                        issue_events.reverse()
                        for ev in issue_events:
                            if "created_at" in ev and "event" in ev and "actor" in ev:
                                eve = {"case:owner": owner, "case:repo": owner+"/"+repo, "case:concept:name": timeline_url, "time:timestamp": strpfromiso.fix_naivety(parse(ev["created_at"])), "concept:name": ev["event"], "org:resource": ev["actor"]["login"], "case:author_association": i["author_association"], "case:title": i["title"]}
                                if "pull_request" in i:
                                    eve["case:pull_request"] = i["pull_request"]["url"]
                                events.append(eve)
                        if progress is not None:
                            progress.update()
            if progress is not None:
                progress.close()
            time.sleep(1)
        except:
            continuee = False
            traceback.print_exc()
            if progress is not None:
                progress.close()
            break

    dataframe = pandas_utils.instantiate_dataframe(events)
    if len(dataframe) > 0:
        dataframe = pandas_utils.insert_index(dataframe, "@@index", copy_dataframe=False, reset_index=False)
        dataframe = dataframe.sort_values(["time:timestamp", "@@index"])
        dataframe["@@case_index"] = dataframe.groupby("case:concept:name", sort=False).ngroup()
        dataframe = dataframe.sort_values(["@@case_index", "time:timestamp", "@@index"])
    return dataframe
