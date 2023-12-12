import pandas as pd
from enum import Enum
from pm4py.util import exec_utils, constants, xes_constants
from typing import Optional, Dict, Any, Union, List, Tuple
from pm4py.objects.log.obj import EventLog
from pm4py.objects.dcr.semantics import DCRSemantics
from pm4py.objects.dcr.obj import DcrGraph
from pm4py.objects.dcr.roles.obj import RoledcrGraph
from pm4py.algo.conformance.dcr.decorators.decorator import ConcreteChecker
from pm4py.algo.conformance.dcr.decorators.roledecorator import RoleDecorator



class Parameters(Enum):
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY

class Outputs(Enum):
    FITNESS = "dev_fitness"
    DEVIATIONS = "deviations"
    NO_DEV_TOTAL = "no_dev_total"
    NO_CONSTR_TOTAL = 'no_constr_total'
    IS_FIT = "is_fit"


class RuleBasedConformance:
    """
        The RoleBasedConformance class provides a simplified interface to perform Rule based conformance check for DCR graphs
        abstract the complexity of direct interaction with the underlying classes:
            - CheckConditions
            - CheckResponses
            - CheckExcludes
            - CheckIncludes
            - CheckRoles,

        RuleBasedConformance is initialized, with the DCR graph to be analyzed, The event log to be replayed,
        Optional parameters can also be passed to customize the processing, such as specifying custom activity
        and case ID keys.

        After initialization of RuleBasedConformance class, user can call apply_conformance(),
        where the DCR Graph will replay the provided event log. Once replay is done,
        returns a list of conformance results for each trace, such as fitness, and the deviations

        Example usage:



        Note:
        - The user is expected to have a base understanding of DCR Graphs and rule based conformance checking in context of process mining

        Attributes:
            DCR Graph: The DCR graph to be checked
            Event log: The event log to be replayed
            Checker (HandleChecker): handler for the conformance checkers for each rule.
            Semantics (DCRSemantics()): The semantics used executing events from the event log
            Parameters: optinal parameters given by the user

        Methods:
            apply_conformance(): performs the replay and computing of conformance of each trace
        """

    def __init__(self, log: Union[EventLog, pd.DataFrame], graph: Union[DcrGraph, RoledcrGraph],
                 parameters: Optional[Dict[Union[str, Any], Any]] = None):
        self.__g = graph
        if isinstance(log, pd.DataFrame):
            log = self.__transform_pandas_dataframe(log, exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters,
                                                                                    constants.CASE_CONCEPT_NAME))
        self.__log = log
        self.__checker = HandleChecker(graph)
        self.__semantics = DCRSemantics()
        self.__parameters = parameters

    def apply_conformance(self) -> List[Dict[str, Any]]:
        """
        Apply Rule based conformance against a DCR Graph, replays the event log using the DCR graph.
        A DCR Graph will before each execution, check for deviations if the current event to be executed is enabled
        or if DCR graph contains roles, if events are executed by the correct roles.
        Will for each replay of trace check if DCR graph is in an accepting state, if not it determines cause.

        For each replay it compute the fitness of the trace

        implementation based on the theory provided in [1],
        and inspired by the Github implementation of conformance checking using trace replay on a DCR graph [2].

        Returns
        ----------
        :return: List containing dictionaries with the following keys and values:
            - no_constr_total: the total number of constraints of the DCR Graphs
            - deviations: the list of deviations
            - no_dev_total: the total number of deviations
            - dev_fitness: the fitness (1 - no_dev_total / no_constr_total),
            - is_fit: True if the case is perfectly fit
        :rtype: List[Dict[str, Any]]

        References
        ----------
        * [1] C. Josep et al., "Conformance Checking Software",  Springer International Publishing, 65-74, 2018. `DOI <https://doi.org/10.1007/978-3-319-99414-7>`_.
        * [2] Sebastian Dunzer, `<https://github.com/fau-is/cc-dcr/tree/master>`_.

        """

        # Create list for accumalating each trace data for conformance
        conf_case = []

        # number of constraints (the relations between activities)
        total_num_constraints = self.__g.get_constraints()

        # get activity key
        activity_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_ACTIVITY_KEY, self.__parameters,
                                                  xes_constants.DEFAULT_NAME_KEY)

        initial_marking = {'executed': set(), 'included': set(), 'pending': set()}
        initial_marking['included'] = set(self.__g.marking.included)
        initial_marking['executed'] = set(self.__g.marking.executed)
        initial_marking['pending'] = set(self.__g.marking.pending)

        # iterate through all traces in log
        for trace in self.__log:
            # create base dict to accumalate trace conformance data
            ret = {Outputs.NO_CONSTR_TOTAL.value: total_num_constraints, Outputs.DEVIATIONS.value: []}
            # execution_his for checking dynamic excludes
            self.__parameters['executionHistory'] = []
            # response_originator for checking reason for not accepting state
            response_origin = []
            # iterate through all events in a trace
            for event in trace:
                # get the event to be executed
                e = self.__g.get_event(event[activity_key])
                self.__parameters['executionHistory'].append(e)

                # check for deviations
                if e in self.__g.responses:
                    for response in self.__g.responses[e]:
                        response_origin.append((e, response))

                self.__checker.all_checker(e, event, self.__g, ret[Outputs.DEVIATIONS.value],
                                           parameters=self.__parameters)

                if not self.__semantics.is_enabled(e, self.__g):
                    self.__checker.enabled_checker(e, self.__g, ret[Outputs.DEVIATIONS.value],
                                                   parameters=self.__parameters)

                # execute the event
                self.__semantics.execute(self.__g, e)

                if len(response_origin) > 0:
                    for i in response_origin:
                        if e == i[1]:
                            response_origin.remove(i)

            # check if run is accepting
            if not self.__semantics.is_accepting(self.__g):
                self.__checker.accepting_checker(self.__g, response_origin, ret[Outputs.DEVIATIONS.value],
                                                 parameters=self.__parameters)

            # compute the conformance for the trace
            ret[Outputs.NO_DEV_TOTAL.value] = len(ret[Outputs.DEVIATIONS.value])
            ret[Outputs.FITNESS.value] = 1 - ret[Outputs.NO_DEV_TOTAL.value] / ret[Outputs.NO_CONSTR_TOTAL.value]
            ret[Outputs.IS_FIT.value] = ret[Outputs.NO_DEV_TOTAL.value] == 0
            conf_case.append(ret)

            # reset graph
            self.__g.marking.reset(initial_marking.copy())

        return conf_case

    def __transform_pandas_dataframe(self, dataframe: pd.DataFrame, case_id_key: str):
        """
        Transforms a pandas DataFrame into a list of event logs grouped by cases.
        Uses a snippet from __transform_dataframe_to_event_stream_new as template to transform pandas dataframe

        This function takes a pandas DataFrame where each row represents an event and converts it into a
        list of lists, where each inner list contains all events related to a single case. The grouping
        of events into cases is based on the case identifier specified by the 'case_id_key' parameter.

        Parameters:
        - dataframe (pd.DataFrame): The pandas DataFrame to be transformed.
        - case_id_key (str): The column name in the DataFrame that acts as the case identifier.

        Returns:
        - list: A list of event logs, where each event log is a list of events (dictionaries)
                corresponding to a single case.

        Each event in the event log is represented as a dictionary, where the keys are the column names
        from the DataFrame and the values are the corresponding values for that event.
        """
        list_events = []
        columns_names = list(dataframe.columns)
        columns_corr = []
        log = []
        last_case_key = dataframe.iloc[0][case_id_key]
        for c in columns_names:
            columns_corr.append(dataframe[c].to_numpy())
        length = columns_corr[-1].size
        for i in range(length):
            event = {}
            for j in range(len(columns_names)):
                event[columns_names[j]] = columns_corr[j][i]
            if last_case_key != event[case_id_key]:
                log.append(list_events)
                list_events = []
            last_case_key = event[case_id_key]
            list_events.append(event)
        log.append(list_events)
        return log


class HandleChecker:
    """
    HandleChecker is responsible for the constructing and calling the associated conformance checker
    for the replay algorithm. This class provides the functionalities to check conformance,
    retrieves the underlying methods for rule checking deviations

    The handle checker is provided the DCR graphs, to construct the collection of methods used for conformance checking

    Attributes
    -----------
    Checker: :class:`pm4py.algo.conformance.dcr.decorators.decorator.Checker`
        The Checker to be used to compute and determine deviations during replay

    Methods
    -----------
    enabled_checker(event, graph, deviations, parameters) -> None:
        Checks for deviations when an activity is not enabled in the DCR Graphs

    all_checker(event, event_attributes, graph, deviations, parameters) -> None:
        Check for deviations that can happen when the rule is not dependent on events being enabled

    accepting_checker(graph, response_origin, deviations, parameters) -> None:
        Checks for deviations that caused the DCR Graphs to be in an unaccepted State after replay

    Parameters
    ----------
    graph: Union[DcrGraph, RoledcrGraph]
        DCR graph
    """

    def __init__(self, graph: Union[DcrGraph, RoledcrGraph]):
        """
        Constructs the CheckHandler, uses the decorator to add functionality depending on input Graph
            - DCR_Graph construct standard checker
            - RoleDCR_Graph Decorate standard checker with Role Checking functionality
        Parameters
        ----------
        graph: Union[DcrGraph, RoledcrGraph]
            DCR Graph
        """
        self.checker = ConcreteChecker()
        # check for additional attributes in dcr, instantiate decorator associated
        if hasattr(graph, 'roles'):
            self.checker = RoleDecorator(self.checker)

    def enabled_checker(self, event: str, graph: Union[DcrGraph, RoledcrGraph], deviations: List[Any],
                        parameters: Optional[Dict[Any, Any]] = None) -> None:
        """
        Enabled checker called when event is not enabled for execution in trace
        Parameters
        ----------
        event: str
            Current event in trace
        graph: Union[DcrGraph, RoledcrGraph]
            DCR Graph
        deviations: List[Any]
            List of deviations
        parameters: Optional[Dict[Any, Any]]
            Optional parameters
        """
        self.checker.enabled_checker(event, graph, deviations, parameters=parameters)

    def all_checker(self, event: str, event_attributes: Dict, graph: Union[DcrGraph, RoledcrGraph], deviations: List[Any],
                    parameters: Optional[Dict[Any, Any]] = None) -> None:
        """
        All checker called for each event in trace to check if any deviation happens regardless of being enabled

        Parameters
        ----------
        event: str
            Current event in trace
        event_attributes: Dict
            All event information used for conformance checking
        graph: Union[DcrGraph, RoledcrGraph]
            DCR Graph
        deviations: List[Any]
            List of deviations
        parameters: Optional[Dict[Any, Any]]
            Optional parameters

        """
        self.checker.all_checker(event, event_attributes, graph, deviations, parameters=parameters)

    def accepting_checker(self, graph: Union[DcrGraph, RoledcrGraph], response_origin: List[Tuple[str,str]],
                          deviations: List[Any], parameters: Optional[Dict[Any, Any]] = None) -> None:
        """
        Accepting checker, called when the DCR graph at the end of trace execution is not not accepting

        Parameters
        ----------
        graph: Union[DcrGraph, RoledcrGraph]
            DCR Graph
        response_origin
        deviations: List[Any]
            List of deviations
        parameters: Optional[Dict[Any, Any]]
            Optional parameters
        """
        self.checker.accepting_checker(graph, response_origin, deviations, parameters=parameters)


def apply(log: Union[pd.DataFrame, EventLog], graph: Union[DcrGraph, RoledcrGraph],
          parameters: Optional[Dict[Any, Any]] = None):
    """
    Applies rule based conformance checking against a DCR graph and an event log.
    Replays the entire log, executing each event and store potential deviations based on set rules associated with the DCR graph.

    implementation based on the theory provided in [1]_,
    and inspired by the Github implementation of conformance checking using trace replay on a DCR graph [2]_.

    Parameters
    -----------
    :param log: pd.DataFrame | EventLog
        event log as :class: `EventLog` or as pandas Dataframe
    :param graph: DCR_Graph | RoleDCR_Graph
        DCR Graph
    :param parameters: Optional[Dict[Any, Any]]
        Possible parameters of the algorithm, including:
            - Parameters.ACTIVITY_KEY => the attribute to be used as activity
            - Parameters.CASE_ID_KEY => the attribute to be used as case identifier
            - Parameters.GROUP_KEY => the attribute to be used as role identifier

    Returns
    ----------
    :return: List containing dictionaries with the following keys and values:
        - no_constr_total: the total number of constraints of the DCR Graphs
        - deviations: the list of deviations
        - no_dev_total: the total number of deviations
        - dev_fitness: the fitness (1 - no_dev_total / no_constr_total),
        - is_fit: True if the case is perfectly fit

    References
    ----------
    .. [1] C. Josep et al., "Conformance Checking Software",
      	Springer International Publishing, 65-74, 2018. `DOI <https://doi.org/10.1007/978-3-319-99414-7>`_.
    .. [2] Sebastian Dunzer, 'Link <https://github.com/fau-is/cc-dcr/tree/master>.

    """
    if parameters is None:
        parameters = {}
    con = RuleBasedConformance(log, graph, parameters=parameters)
    return con.apply_conformance()


def get_diagnostics_dataframe(log: Union[EventLog, pd.DataFrame], conf_result: List[Dict[str, Any]],
                              parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    """
    Gets the diagnostics dataframe from a log and the results of conformance checking of DCR graph

    Applies the same functionality as log_skeleton and declare

    Parameters
    ---------------
    :param log: event log as :class: `EventLog` or as pandas Dataframe
    :param conf_result: Results of conformance checking
    :param parameters: Optional Parameter to specify case id key

    Returns
    ---------------
    :return: Diagnostics dataframe
    """

    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters,
                                             xes_constants.DEFAULT_TRACEID_KEY)

    import pandas as pd
    diagn_stream = []
    for index in range(len(log)):
        case_id = log[index].attributes[case_id_key]
        no_dev_total = conf_result[index][Outputs.NO_DEV_TOTAL.value]
        no_constr_total = conf_result[index][Outputs.NO_CONSTR_TOTAL.value]
        dev_fitness = conf_result[index][Outputs.FITNESS.value]

        diagn_stream.append({"case_id": case_id, "no_dev_total": no_dev_total, "no_constr_total": no_constr_total,
                             "dev_fitness": dev_fitness})

    return pd.DataFrame(diagn_stream)
