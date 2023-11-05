import pandas as pd
from copy import deepcopy
from pm4py.util import exec_utils, constants, xes_constants
from typing import Optional, Dict, Any, Union, List

from pm4py.objects.log.obj import EventLog

from pm4py.objects.dcr.semantics import DCRSemantics

from pm4py.algo.conformance.dcr.decorators.decorator import ConcreteChecker
from pm4py.algo.conformance.dcr.decorators.roledecorator import RoleDecorator

from pm4py.objects.dcr.obj import DCR_Graph


class RuleBasedConformance:
    def __init__(self, checker, semantics):
        self.__checker = checker
        self.__semantics = semantics

    def apply_conformance(self, log: Union[EventLog, List[List[dict]]], G: DCR_Graph,
                          parameters: Optional[Dict[Union[str, Any], Any]] = None) -> List[Dict[str, Any]]:
        """
        The main rule based conformance algorithm

        :param log: event log as a List of lists containing the events with relevant attributes
        :param G: a DCR graph
        :param parameters: Optional parameters use for defining the attributes of an event

        :return: a list of dictionaries containing the conformance results of each trace
        :rtype: List[Dict[str, Any]]
        """
        # Create list for accumalating each trace data for conformance
        conf_case = []

        # number of constraints (the relations between activities)
        total_num_constraints = G.getConstraints()

        # get activity key
        activity_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_ACTIVITY_KEY, parameters,
                                                  xes_constants.DEFAULT_NAME_KEY)

        initial_marking = deepcopy(G.marking)
        # iterate through all traces in log
        for trace in log:
            # reset dcr graph
            G.marking.reset(deepcopy(initial_marking))
            # create base dict to accumalate trace conformance data
            ret = {'no_constr_total': total_num_constraints, 'deviations': []}

            response_origin = []
            # iterate through all events in a trace
            for event in trace:
                # get the event to be executed
                e = G.getEvent(event[activity_key])

                # check for deviations
                if e in G.responseTo:
                    for response in G.responseTo[e]:
                        response_origin.append([e, response])

                self.__checker.all_checker(e, event, G, ret['deviations'], parameters=parameters)

                if not self.__semantics.is_enabled(e, G):
                    self.__checker.enabled_checker(e, G, ret['deviations'], parameters=parameters)

                # execute the event
                G = self.__semantics.execute(G, e)

                if len(response_origin) > 0:
                    for i in response_origin:
                        if e == i[1]:
                            response_origin.remove(i)

            # check if run is accepting
            if not self.__semantics.is_accepting(G):
                self.__checker.accepting_checker(G, response_origin, ret['deviations'], parameters=parameters)

            # compute the conformance for the trace
            ret["no_dev_total"] = len(ret["deviations"])
            ret["dev_fitness"] = 1 - ret["no_dev_total"] / ret["no_constr_total"]
            ret["is_fit"] = ret["no_dev_total"] == 0
            conf_case.append(ret)

        return conf_case


def apply(log: Union[pd.DataFrame, EventLog], dcr,
          parameters: Optional[Dict[Union[str, Any], Any]] = None, additional: bool = False):
    """
    Applies rule based conformance checking against a DCR graph and an event log.
    Replays the entire log, executing each event and store potential deviations based on set rules associated with the DCR graph.

    implementation based on the theory provided in [1]_,
    and inspired by the Github implementation of conformance checking using trace replay on a DCR graph [2]_.

    Parameters
    ---------------
    :param log: event log as :class: `EventLog` or as pandas Dataframe
    :param dcr: DCR Graph
    :param parameters: Possible parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => the attribute to be used as activity
        - Parameters.CASE_ID_KEY => the attribute to be used as case identifier
        - Parameters.GROUP_KEY => the attribute to be used as role identifier

    Returns
    ---------------
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
    .. [2] Sebastian Dunzer, 'Link <https://github.com/fau-is/cc-dcr/tree/master>

    """
    if parameters is None:
        parameters = {}

    if isinstance(log, pd.DataFrame):
        return __apply_Pandas(log, dcr, parameters=parameters)

    return __apply_log(log, dcr, parameters=parameters)


def __apply_log(log, dcr, parameters: Optional[Dict[Union[str, Any], Any]] = None):
    # instantiate the basic checker and decorator for conformance checking
    checker = ConcreteChecker()
    sem = DCRSemantics()

    # check for additional attributes in dcr, instantiate decorator associated
    if hasattr(dcr, 'roles'):
        checker = RoleDecorator(checker)

    # instantiate conformance checking
    con = RuleBasedConformance(checker, sem)
    return con.apply_conformance(log, dcr, parameters)


def __apply_Pandas(log, dcr, parameters: Optional[Dict[Union[str, Any], Any]]):
    # if log is pandas dataframe, needs to be converted to a list of lists
    activity_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_ACTIVITY_KEY, parameters,
                                              xes_constants.DEFAULT_NAME_KEY)
    case_id_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_CASEID_KEY, parameters,
                                             constants.CASE_CONCEPT_NAME)

    # base log
    new_log = log[[activity_key, case_id_key]]
    # instantiate checker and semantics used for conformance checking
    checker = ConcreteChecker()
    sem = DCRSemantics()

    # check for additional attributes in dcr
    # instantiate decorator associated and append additional column with associated values
    if hasattr(dcr, 'roles'):
        group_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_GROUP_KEY, parameters,
                                                  xes_constants.DEFAULT_GROUP_KEY)
        new_log.insert(len(new_log.keys()), group_key, log[group_key], True)
        checker = RoleDecorator(checker)

    log = __transform_pandas_dataframe(new_log, case_id_key)

    con = RuleBasedConformance(checker, sem)

    # call apply conformance
    return con.apply_conformance(log, dcr, parameters)


def __transform_pandas_dataframe(dataframe, case_id_key):
    # uses a snippet from __transform_dataframe_to_event_stream_new as template to transform pandas dataframe
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


def get_diagnostics_dataframe(log: Union[EventLog, pd.DataFrame], conf_result: List[Dict[str, Any]],
                              parameters=None) -> pd.DataFrame:
    """
    Gets the diagnostics dataframe from a log and the results of conformance checking of DCR graph

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

    case_id_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_CASEID_KEY, parameters,
                                             xes_constants.DEFAULT_TRACEID_KEY)
    import pandas as pd

    diagn_stream = []

    for index in range(len(log)):
        case_id = log[index].attributes[case_id_key]
        no_dev_total = conf_result[index]["no_dev_total"]
        no_constr_total = conf_result[index]["no_constr_total"]
        dev_fitness = conf_result[index]["dev_fitness"]

        diagn_stream.append({"case_id": case_id, "no_dev_total": no_dev_total, "no_constr_total": no_constr_total,
                             "dev_fitness": dev_fitness})

    return pd.DataFrame(diagn_stream)
