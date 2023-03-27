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

from typing import Optional
import pandas as pd
from pm4py.objects.ocel.obj import OCEL


def extract_log_outlook_mails() -> pd.DataFrame:
    """
    Extracts the history of the conversations from the local instance of Microsoft Outlook
    running on the current computer.

    CASE ID (case:concept:name) => identifier of the conversation
    ACTIVITY (concept:name) => activity that is performed in the current item (send e-mail, receive e-mail,
                                                                                refuse meeting ...)
    TIMESTAMP (time:timestamp) => timestamp of creation of the item in Outlook
    RESOURCE (org:resource) => sender of the current item

    See also:
    * https://learn.microsoft.com/en-us/dotnet/api/microsoft.office.interop.outlook.mailitem?redirectedfrom=MSDN&view=outlook-pia#properties_
    * https://learn.microsoft.com/en-us/dotnet/api/microsoft.office.interop.outlook.olobjectclass?view=outlook-pia

    :rtype: ``pd.DataFrame``

    .. code-block:: python3
        import pm4py

        dataframe = pm4py.connectors.extract_log_outlook_mails()
    """
    from pm4py.algo.connectors.variants import outlook_mail_extractor
    return outlook_mail_extractor.apply()


def extract_log_outlook_calendar(email_user: Optional[str] = None, calendar_id: int = 9) -> pd.DataFrame:
    """
    Extracts the history of the calendar events (creation, update, start, end)
    in a Pandas dataframe from the local Outlook instance running on the current computer.

    CASE ID (case:concept:name) => identifier of the meeting
    ACTIVITY (concept:name) => one between: Meeting Created, Last Change of Meeting, Meeting Started, Meeting Completed
    TIMESTAMP (time:timestamp) => the timestamp of the event
    case:subject => the subject of the meeting

    :param email_user: (optional) e-mail address from which the (shared) calendar should be extracted
    :param calendar_id: identifier of the calendar for the given user (default: 9)

    :rtype: ``pd.DataFrame``

    .. code-block:: python3
        import pm4py

        dataframe = pm4py.connectors.extract_log_outlook_calendar()
        dataframe = pm4py.connectors.extract_log_outlook_calendar("vacation-calendar@workplace.eu")
    """
    from pm4py.algo.connectors.variants import outlook_calendar
    parameters = {}
    parameters[outlook_calendar.Parameters.EMAIL_USER] = email_user
    parameters[outlook_calendar.Parameters.CALENDAR_ID] = calendar_id
    return outlook_calendar.apply(parameters=parameters)


def extract_log_windows_events() -> pd.DataFrame:
    """
    Extract a process mining dataframe from all the events recorded in the Windows registry.

    CASE ID (case:concept:name) => name of the computer emitting the events.
    ACTIVITY (concept:name)  => concatenation of the source name of the event and the event identifier
                (see https://learn.microsoft.com/en-us/previous-versions/windows/desktop/eventlogprov/win32-ntlogevent)
    TIMESTAMP (time:timestamp) => timestamp of generation of the event
    RESOURCE (org:resource) => username involved in the event

    :rtype: ``pd.DataFrame``

    .. code-block:: python3
        import pm4py

        dataframe = pm4py.connectors.extract_log_windows_events()
    """
    from pm4py.algo.connectors.variants import windows_events
    return windows_events.apply()


def extract_log_chrome_history(history_db_path: Optional[str] = None) -> pd.DataFrame:
    """
    Extracts a dataframe containing the navigation history of Google Chrome.
    Please keep Google Chrome history closed when extracting.

    CASE ID (case:concept:name) => an identifier of the profile that has been extracted
    ACTIVITY (concept:name) => the complete path of the website, minus the GET arguments
    TIMESTAMP (time:timestamp) => the timestamp of visit

    :param history_db_path: path to the history DB path of Google Chrome (default: position of the Windows folder)
    :rtype: ``pd.DataFrame``

    .. code-block:: python3
        import pm4py

        dataframe = pm4py.connectors.extract_log_chrome_history()
    """
    from pm4py.algo.connectors.variants import chrome_history
    parameters = {}
    if history_db_path is not None:
        parameters[chrome_history.Parameters.HISTORY_DB_PATH] = history_db_path
    return chrome_history.apply(parameters=parameters)


def extract_log_firefox_history(history_db_path: Optional[str] = None) -> pd.DataFrame:
    """
    Extracts a dataframe containing the navigation history of Mozilla Firefox.
    Please keep Google Chrome history closed when extracting.

    CASE ID (case:concept:name) => an identifier of the profile that has been extracted
    ACTIVITY (concept:name) => the complete path of the website, minus the GET arguments
    TIMESTAMP (time:timestamp) => the timestamp of visit

    :param history_db_path: path to the history DB path of Mozilla Firefox (default: position of the Windows folder)
    :rtype: ``pd.DataFrame``

    .. code-block:: python3
        import pm4py

        dataframe = pm4py.connectors.extract_log_firefox_history()
    """
    from pm4py.algo.connectors.variants import firefox_history
    parameters = {}
    if history_db_path is not None:
        parameters[firefox_history.Parameters.HISTORY_DB_PATH] = history_db_path
    return firefox_history.apply(parameters=parameters)


def extract_log_github(owner: str = "pm4py", repo: str = "pm4py-core", auth_token: Optional[str] = None) -> pd.DataFrame:
    """
    Extracts a dataframe containing the history of the issues of a Github repository.
    According to the API limit rate of public/registered users, only a part of the events
    can be returned.

    :param owner: owner of the repository (e.g., pm4py)
    :param repo: name of the repository (e.g., pm4py-core)
    :param auth_token: authorization token
    :rtype: ``pd.DataFrame``

    .. code-block:: python3
        import pm4py

        dataframe = pm4py.connectors.extract_log_github(owner='pm4py', repo='pm4py-core')
    """
    from pm4py.algo.connectors.variants import github_repo
    parameters = {}
    parameters[github_repo.Parameters.OWNER] = owner
    parameters[github_repo.Parameters.REPOSITORY] = repo
    parameters[github_repo.Parameters.AUTH_TOKEN] = auth_token
    return github_repo.apply(parameters)


def extract_log_camunda_workflow(connection_string: str) -> pd.DataFrame:
    """
    Extracts a dataframe from the Camunda workflow system. Aside from the traditional columns,
    the processID of the process in Camunda is returned.

    :param connection_string: ODBC connection string to the Camunda database
    :rtype: ``pd.DataFrame``

    .. code-block:: python3
        import pm4py

        dataframe = pm4py.connectors.extract_log_camunda_workflow('Driver={PostgreSQL Unicode(x64)};SERVER=127.0.0.3;DATABASE=process-engine;UID=xx;PWD=yy')
    """
    from pm4py.algo.connectors.variants import camunda_workflow
    parameters = {}
    parameters[camunda_workflow.Parameters.CONNECTION_STRING] = connection_string
    return camunda_workflow.apply(None, parameters=parameters)


def extract_log_sap_o2c(connection_string: str, prefix: str = "") -> pd.DataFrame:
    """
    Extracts a dataframe for the SAP O2C process.

    :param connection_string: ODBC connection string to the SAP database
    :param prefix: prefix for the tables (example: SAPSR3.)
    :rtype: ``pd.DataFrame``

    .. code-block:: python3
        import pm4py

        dataframe = pm4py.connectors.extract_log_sap_o2c('Driver={Oracle in instantclient_21_6};DBQ=127.0.0.3:1521/ZIB;UID=xx;PWD=yy')
    """
    from pm4py.algo.connectors.variants import sap_o2c
    parameters = {}
    parameters[sap_o2c.Parameters.CONNECTION_STRING] = connection_string
    parameters[sap_o2c.Parameters.PREFIX] = prefix
    return sap_o2c.apply(None, parameters=parameters)


def extract_log_sap_accounting(connection_string: str, prefix: str = "") -> pd.DataFrame:
    """
    Extracts a dataframe for the SAP Accounting process.

    :param connection_string: ODBC connection string to the SAP database
    :param prefix: prefix for the tables (example: SAPSR3.)
    :rtype: ``pd.DataFrame``

    .. code-block:: python3
        import pm4py

        dataframe = pm4py.connectors.extract_log_sap_accounting('Driver={Oracle in instantclient_21_6};DBQ=127.0.0.3:1521/ZIB;UID=xx;PWD=yy')
    """
    from pm4py.algo.connectors.variants import sap_accounting
    parameters = {}
    parameters[sap_accounting.Parameters.CONNECTION_STRING] = connection_string
    parameters[sap_accounting.Parameters.PREFIX] = prefix
    return sap_accounting.apply(None, parameters=parameters)


def extract_ocel_outlook_mails() -> OCEL:
    """
    Extracts the history of the conversations from the local instance of Microsoft Outlook
    running on the current computer as an object-centric event log.

    ACTIVITY (ocel:activity) => activity that is performed in the current item (send e-mail, receive e-mail,
                                                                                refuse meeting ...)
    TIMESTAMP (ocel:timestamp) => timestamp of creation of the item in Outlook

    Object types:
    - org:resource => the snder of the mail
    - recipients => the list of recipients of the mail
    - topic => the topic of the discussion

    See also:
    * https://learn.microsoft.com/en-us/dotnet/api/microsoft.office.interop.outlook.mailitem?redirectedfrom=MSDN&view=outlook-pia#properties_
    * https://learn.microsoft.com/en-us/dotnet/api/microsoft.office.interop.outlook.olobjectclass?view=outlook-pia

    :rtype: ``OCEL``

    .. code-block:: python3
        import pm4py

        ocel = pm4py.connectors.extract_ocel_outlook_mails()
    """
    import pm4py
    dataframe = pm4py.connectors.extract_log_outlook_mails()
    return pm4py.convert_log_to_ocel(dataframe, "concept:name", "time:timestamp", ["org:resource", "recipients", "topic"])


def extract_ocel_outlook_calendar(email_user: Optional[str] = None, calendar_id: int = 9) -> OCEL:
    """
    Extracts the history of the calendar events (creation, update, start, end)
    as an object-centric event log from the local Outlook instance running on the current computer.

    ACTIVITY (ocel:activity) => one between: Meeting Created, Last Change of Meeting, Meeting Started, Meeting Completed
    TIMESTAMP (ocel:timestamp) => the timestamp of the event

    Object types:
    - case:concept:name => identifier of the meeting
    - case:subject => the subject of the meeting

    :param email_user: (optional) e-mail address from which the (shared) calendar should be extracted
    :param calendar_id: identifier of the calendar for the given user (default: 9)

    :rtype: ``OCEL``

    .. code-block:: python3
        import pm4py

        ocel = pm4py.connectors.extract_ocel_outlook_calendar()
        ocel = pm4py.connectors.extract_ocel_outlook_calendar("vacation-calendar@workplace.eu")
    """
    import pm4py
    dataframe = pm4py.connectors.extract_log_outlook_calendar(email_user, calendar_id)
    return pm4py.convert_log_to_ocel(dataframe, "concept:name", "time:timestamp", ["case:concept:name", "case:subject"])


def extract_ocel_windows_events() -> OCEL:
    """
    Extract a process mining dataframe from all the events recorded in the Windows registry as an object-centric
    event log.

    ACTIVITY (concept:name)  => concatenation of the source name of the event and the event identifier
                (see https://learn.microsoft.com/en-us/previous-versions/windows/desktop/eventlogprov/win32-ntlogevent)
    TIMESTAMP (time:timestamp) => timestamp of generation of the event

    Object types:
    - categoryString: translation of the subcategory. The translation is source-specific.
    - computerName: name of the computer that generated this event.
    - eventIdentifier: identifier of the event. This is specific to the source that generated the event log entry.
    - eventType: 1=Error; 2=Warning; 3=Information; 4=Security Audit Success;5=Security Audit Failure;
    - sourceName: name of the source (application, service, driver, or subsystem) that generated the entry.
    - user: user name of the logged-on user when the event occurred. If the user name cannot be determined, this will be NULL.

    :rtype: ``OCEL``

    .. code-block:: python3
        import pm4py

        ocel = pm4py.connectors.extract_ocel_windows_events()
    """
    import pm4py
    dataframe = pm4py.connectors.extract_log_windows_events()
    return pm4py.convert_log_to_ocel(dataframe, "concept:name", "time:timestamp", ["categoryString", "computerName", "eventIdentifier", "eventType", "sourceName", "user"])


def extract_ocel_chrome_history(history_db_path: Optional[str] = None) -> OCEL:
    """
    Extracts an object-centric event log containing the navigation history of Google Chrome.
    Please keep Google Chrome history closed when extracting.

    ACTIVITY (ocel:activity) => the complete path of the website, minus the GET arguments
    TIMESTAMP (ocel:timestamp) => the timestamp of visit

    Object Types:
    - case:concept:name : the profile of Chrome that is used to visit the site
    - complete_url: the complete URL of the website
    - url_wo_parameters: complete URL minus the part after ?
    - domain: the domain of the website that is visited

    :param history_db_path: path to the history DB path of Google Chrome (default: position of the Windows folder)
    :rtype: ``OCEL``

    .. code-block:: python3
        import pm4py

        dataframe = pm4py.connectors.extract_ocel_chrome_history()
    """
    import pm4py
    dataframe = pm4py.connectors.extract_log_chrome_history(history_db_path)
    return pm4py.convert_log_to_ocel(dataframe, "concept:name", "time:timestamp", ["case:concept:name", "complete_url", "url_wo_parameters", "domain"])


def extract_ocel_firefox_history(history_db_path: Optional[str] = None) -> OCEL:
    """
    Extracts an object-centric event log containing the navigation history of Mozilla Firefox.
    Please keep Mozilla Firefox history closed when extracting.

    ACTIVITY (ocel:activity) => the complete path of the website, minus the GET arguments
    TIMESTAMP (ocel:timestamp) => the timestamp of visit

    Object Types:
    - case:concept:name : the profile of Firefox that is used to visit the site
    - complete_url: the complete URL of the website
    - url_wo_parameters: complete URL minus the part after ?
    - domain: the domain of the website that is visited

    :param history_db_path: path to the history DB path of Mozilla Firefox (default: position of the Windows folder)
    :rtype: ``OCEL``

    .. code-block:: python3
        import pm4py

        dataframe = pm4py.connectors.extract_ocel_firefox_history()
    """
    import pm4py
    dataframe = pm4py.connectors.extract_log_firefox_history(history_db_path)
    return pm4py.convert_log_to_ocel(dataframe, "concept:name", "time:timestamp", ["case:concept:name", "complete_url", "url_wo_parameters", "domain"])


def extract_ocel_github(owner: str = "pm4py", repo: str = "pm4py-core", auth_token: Optional[str] = None) -> OCEL:
    """
    Extracts a dataframe containing the history of the issues of a Github repository.
    According to the API limit rate of public/registered users, only a part of the events
    can be returned.

    ACTIVITY (ocel:activity) => the event (created, commented, closed, subscribed ...)
    TIMESTAMP (ocel:timestamp) => the timestamp of execution of the event

    Object types:
    - case:concept:name => the URL of the events related to the issue
    - org:resource => the involved resource
    - case:repo => the repository in which the issue is created

    :param owner: owner of the repository (e.g., pm4py)
    :param repo: name of the repository (e.g., pm4py-core)
    :param auth_token: authorization token
    :rtype: ``OCEL``

    .. code-block:: python3
        import pm4py

        dataframe = pm4py.connectors.extract_ocel_github(owner='pm4py', repo='pm4py-core')
    """
    import pm4py
    dataframe = pm4py.connectors.extract_log_github(owner, repo, auth_token)
    return pm4py.convert_log_to_ocel(dataframe, "concept:name", "time:timestamp", ["case:concept:name", "org:resource", "case:repo"])


def extract_ocel_camunda_workflow(connection_string: str) -> OCEL:
    """
    Extracts an object-centric event log from the Camunda workflow system.

    :param connection_string: ODBC connection string to the Camunda database
    :rtype: ``pd.DataFrame``

    .. code-block:: python3
        import pm4py

        ocel = pm4py.connectors.extract_ocel_camunda_workflow('Driver={PostgreSQL Unicode(x64)};SERVER=127.0.0.3;DATABASE=process-engine;UID=xx;PWD=yy')
    """
    import pm4py
    dataframe = pm4py.connectors.extract_log_camunda_workflow(connection_string)
    return pm4py.convert_log_to_ocel(dataframe, "concept:name", "time:timestamp", ["case:concept:name", "processID", "org:resource"])


def extract_ocel_sap_o2c(connection_string: str, prefix: str = '') -> OCEL:
    """
    Extracts an object-centric event log for the SAP O2C process.

    :param connection_string: ODBC connection string to the SAP database
    :param prefix: prefix for the tables (example: SAPSR3.)
    :rtype: ``pd.DataFrame``

    .. code-block:: python3
        import pm4py

        dataframe = pm4py.connectors.extract_ocel_sap_o2c('Driver={Oracle in instantclient_21_6};DBQ=127.0.0.3:1521/ZIB;UID=xx;PWD=yy')
    """
    import pm4py
    dataframe = pm4py.connectors.extract_log_sap_o2c(connection_string, prefix=prefix)
    return pm4py.convert_log_to_ocel(dataframe, "concept:name", "time:timestamp", ["case:concept:name", "org:resource"])


def extract_ocel_sap_accounting(connection_string: str, prefix: str = '') -> OCEL:
    """
    Extracts an object-centric event log for the SAP Accounting process.

    :param connection_string: ODBC connection string to the SAP database
    :param prefix: prefix for the tables (example: SAPSR3.)
    :rtype: ``pd.DataFrame``

    .. code-block:: python3
        import pm4py

        dataframe = pm4py.connectors.extract_ocel_sap_accounting('Driver={Oracle in instantclient_21_6};DBQ=127.0.0.3:1521/ZIB;UID=xx;PWD=yy')
    """
    import pm4py
    dataframe = pm4py.connectors.extract_log_sap_accounting(connection_string, prefix=prefix)
    return pm4py.convert_log_to_ocel(dataframe, "concept:name", "time:timestamp", ["case:concept:name", "org:resource"])
