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

import pandas as pd
from typing import Optional, Dict, Any


AVAILABLE_CONNECTORS = ["chrome_history", "firefox_history", "github_repo", "outlook_calendar", "outlook_mail_extractor",
                        "windows_events", "camunda_workflow", "sap_accounting", "sap_o2c"]


def apply(type: str, args: Dict[Any, Any] = None, parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    if args is None:
        args = {}

    if parameters is None:
        parameters = {}

    conn = args["conn"] if "conn" in args else None

    if type == "chrome_history":
        from pm4py.algo.connectors.variants import chrome_history
        return chrome_history.apply(parameters=parameters)
    elif type == "firefox_history":
        from pm4py.algo.connectors.variants import firefox_history
        return firefox_history.apply(parameters=parameters)
    elif type == "github_repo":
        from pm4py.algo.connectors.variants import github_repo
        return github_repo.apply(parameters=parameters)
    elif type == "outlook_calendar":
        from pm4py.algo.connectors.variants import outlook_calendar
        return outlook_calendar.apply(parameters=parameters)
    elif type == "outlook_mail":
        from pm4py.algo.connectors.variants import outlook_mail_extractor
        return outlook_mail_extractor.apply(parameters=parameters)
    elif type == "windows_events":
        from pm4py.algo.connectors.variants import windows_events
        return windows_events.apply(parameters=parameters)
    elif type == "camunda_workflow":
        from pm4py.algo.connectors.variants import camunda_workflow
        return camunda_workflow.apply(conn, parameters=parameters)
    elif type == "sap_accounting":
        from pm4py.algo.connectors.variants import sap_accounting
        return sap_accounting.apply(conn, parameters=parameters)
    elif type == "sap_o2c":
        from pm4py.algo.connectors.variants import sap_o2c
        return sap_o2c.apply(conn, parameters=parameters)
