from typing import Optional, Dict, Any
import win32com.client
import pandas as pd
from datetime import datetime
import pkgutil
import traceback


def apply(parameters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Extract a process mining dataframe from all the events recorded in the Windows registry.

    CASE ID (case:concept:name) => name of the computer emitting the events.
    ACTIVITY (concept:name)  => concatenation of the source name of the event and the event identifier
                (see https://learn.microsoft.com/en-us/previous-versions/windows/desktop/eventlogprov/win32-ntlogevent)
    TIMESTAMP (time:timestamp) => timestamp of generation of the event
    RESOURCE (org:resource) => username involved in the event

    Returns
    ----------------
    dataframe
        Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    print(":: executing SQL query against the Windows registry. this can take time.")

    strComputer = "."
    objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    objSWbemServices = objWMIService.ConnectServer(strComputer, "root\cimv2")
    colItems = objSWbemServices.ExecQuery("Select * from Win32_NTLogEvent")
    events = []

    progress = None
    if pkgutil.find_loader("tqdm"):
        from tqdm.auto import tqdm
        progress = tqdm(total=len(colItems),
                        desc="extracting Windows events, progress :: ")

    for objItem in colItems:
        events.append({"category": str(objItem.Properties_("Category")), "categoryString": str(objItem.Properties_("CategoryString")),
                       "computerName": str(objItem.Properties_("ComputerName")), "eventCode": str(objItem.Properties_("EventCode")),
                       "eventIdentifier": str(objItem.Properties_("EventIdentifier")), "eventType": str(objItem.Properties_("EventType")),
                       "logFile": str(objItem.Properties_("LogFile")), "message": str(objItem.Properties_("Message")),
                       "recordNumber": str(objItem.Properties_("RecordNumber")),
                       "sourceName": str(objItem.Properties_("SourceName")),
                       "timeGenerated": datetime.strptime(str(str(objItem.Properties_("TimeGenerated"))).split("+")[0].split("-")[0], "%Y%m%d%H%M%S.%f"),
                       "timeWritten": datetime.strptime(str(str(objItem.Properties_("TimeWritten"))).split("+")[0].split("-")[0], "%Y%m%d%H%M%S.%f"),
                       "type": str(str(objItem.Properties_("Type"))), "user": str(str(objItem.Properties_("User")))})
        if progress is not None:
            progress.update()

    if progress is not None:
        progress.close()

    dataframe = pd.DataFrame(events)
    dataframe["case:concept:name"] = dataframe["computerName"]
    dataframe["time:timestamp"] = dataframe["timeGenerated"]
    dataframe["concept:name"] = dataframe["sourceName"] + " " + dataframe["eventIdentifier"]
    dataframe["org:resource"] = dataframe["user"]
    dataframe["@@index"] = dataframe.index
    dataframe = dataframe.sort_values(["time:timestamp", "@@index"])
    dataframe["@@case_index"] = dataframe.groupby("case:concept:name", sort=False).ngroup()
    dataframe = dataframe.sort_values(["@@case_index", "time:timestamp", "@@index"])

    return dataframe
