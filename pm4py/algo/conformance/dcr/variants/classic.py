import pm4py
from pm4py.objects.log.obj import EventLog
from pm4py.objects.dcr.obj import DCR_Graph, Relations
from pm4py.objects.dcr.roles.obj import RoleDCR_Graph
from pm4py.objects.dcr.semantics import DCRSemantics
from pm4py.util import exec_utils, constants, xes_constants
from typing import Optional, Dict, Any, Union
from collections import Counter
import pandas as pd
from copy import deepcopy

class RuleBasedConformance:
    def __excludeViolation(self, act, model, ret):
        # if an acitivty has been excluded, but trace tries to execute, exclude violation
        if act not in model.marking.included:
            ret['deviations'].append(['excludeViolation', act])


    def __conditionViolation(self, act, model, ret):
        # we check if conditions for activity has been executed, if not, that's a conditions violation
        # check if act is in conditions for
        if act in model.conditionsFor:
            #check the conditions for event act
            for e in model.conditionsFor[act]:
                # if conditions are included and not executed, add violation
                if e not in model.marking.included.intersection(model.marking.executed):
                    ret['deviations'].append(['conditionViolation', (e, act)])



    def __responseViolation(self, model, ret, responseEvent):
        # if activities are pending, and included, thats a response violation
        for e in model.marking.included.intersection(model.marking.pending):

            ret['deviations'].append(['response', e])


    def __roleViolation(self, event, model, ret, parameters):
        #get the parameters
        role_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_ROLE_KEY, parameters,
                                              xes_constants.DEFAULT_ROLE_KEY)
        resource_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_RESOURCE_KEY, parameters,
                                              xes_constants.DEFAULT_RESOURCE_KEY)
        activity_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY, parameters,
                                              xes_constants.DEFAULT_NAME_KEY)

        if role_key in event.keys():
            # checks if event role is NaN
            # if thats the case, anyone can perform this action
            if event[role_key] != event[role_key]:
                return 0

            #if role is performed by a role not registered thats a violation
            if event[role_key] not in model.roles:
                #if role doesn't exist, means that they dont have athourity to perform the action
                ret['deviations'].append(['RoleViolating', event[role_key]])
                return 0
            else:
                # if role exist
                # violation when:
                # 1) when as role has not be assigned (P,act)
                # 2) when role has not be assigned act
                # 3) when role has not be assigned P
                res = model.roleAssignment[event[role_key]].intersection({(event[resource_key], event[activity_key])})
                if not res:
                    ret['deviations'].append(['RoleViolating', (event[role_key],event[resource_key],event[activity_key])])
                return 0

        else:
            #checks if resource is in roles
            if event[resource_key] not in model.roles:
                #if role doesn't exist, means that they dont have athourity to perform the action
                ret['deviations'].append(['RoleViolating', event[resource_key]])
                return 0
            else:
                # if role exist
                # violation when:
                # 1) when as role has not be assigned act
                res = model.roleAssignment[event[resource_key]].intersection({event[activity_key]})
                if not res:
                    ret['deviations'].append(['RoleViolating', (event[resource_key],event[activity_key])])
                return 0

    def __no_of_rules(self, dcr):
        relations = [e.value for e in Relations]
        no = 0
        #allows for dictionary
        for i in relations:
            for j in dcr[i]:
                no += len(dcr[i][j])
        return no


    def apply_conformance(self, log: Union[pd.DataFrame, EventLog], dcr: [DCR_Graph, RoleDCR_Graph], parameters):
        conf_case = []
        #number of constraints
        #the relations between activities
        total_num_constraints = self.__no_of_rules(dcr)
        #load in the parameter to be used
        # todo, figure out what to do with roles
        activity_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
        case_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_CASEID_KEY, parameters, constants.CASE_CONCEPT_NAME)
        #if case of pandas dataframe, convert it to a list of traces
        if isinstance(log, pd.DataFrame):
            log = log.groupby(case_key).apply(lambda x: x.to_dict(orient='records'))

        #initiate class for DCR graph semantics
        sem = DCRSemantics()
        #iterate through all traces in a log

        for trace in log:
            # initiate a dictionary to collect all deviation and their type
            ret = {'no_constr_total': total_num_constraints, 'deviations': [], 'event_counter': Counter()}
            # instantiate a new model to perform execution on
            model = deepcopy(dcr)
            # count id to find placement in trace, the role deviated
            countID = 0

            # event casuing a execution to be pending
            responseEvent = []
            # iterate through all events in a trace
            for event in trace:
                #get the activity to be performed
                act = event[activity_key]
                ret['event_counter'].update([act])
                #if else conditions to check if activity is enabled for execution

                if event[activity_key] not in sem.enabled(model):
                    #collection type of violation
                    self.__conditionViolation(act, model, ret)
                    self.__excludeViolation(act, model, ret)

                if len(model['roles']) > 0:
                    self.__roleViolation(event, model, ret, parameters)
                    """
                    #possible insert more functions here to extend if possible:
                    """
                #if pending event exist
                if act in model.responseTo:
                    responses = model.responseTo[act]
                    if responses:
                        responseEvent.append(responses)
                    model = sem.execute(model, act)
                    countID += 1

            #when all events in trace has been executed, check if model is accepting
            if not sem.is_accepting(model):

                #if not, get activities violating the response rule
                self.__responseViolation(model, ret, responseEvent)

            #collect the fitness of the trace
            ret["no_dev_total"] = len(ret["deviations"])
            ret["dev_fitness"] = 1 - ret["no_dev_total"] / ret["no_constr_total"]
            ret["is_fit"] = ret["no_dev_total"] == 0

            #append the result to conf_case
            conf_case.append(ret)


        return conf_case


def apply(log: Union[pd.DataFrame, EventLog], dcr: DCR_Graph,
          parameters: Optional[Dict[Any, Any]]):
    """
    Applies conformance checking against a DCR graph

    implementation based on rule-checking from:


    and inspired by implementation in github:

    Returns the same kind of data type and structure as conformance for declare and log skeleton

    Parameters
    ---------------
    log
        event log
    dcr
        DCR Graph
    parameters
        Possible parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => the attribute to be used as activity
        - Parameters.CASE_ID_KEY => the attribute to be used as case identifier
        - Parameters.ROLE_KEY => the attribyte to be used as role identifier

    Returns
    ---------------
    traces
        List containing for every case a dictionary with different keys:
        - no_constr_total => the total number of constraints of the DECLARE model
        - deviations => a list of deviations
        - no_dev_total => the total number of deviations
        - dev_fitness => the fitness (1 - no_dev_total / no_constr_total)
        - is_fit => True if the case is perfectly fit
    """
    #if no parameters are given, initiate empty dictionary
    if parameters is None:
        parameters = {}

    # instantiate class
    con = RuleBasedConformance()

    # call apply conformance
    traces = con.apply_conformance(log, dcr, parameters=parameters)

    return traces


def get_diagnostics_dataframe(log, conf_result, parameters=None) -> pd.DataFrame:
    """
    Implemented to provide the same diagnositcs dataframe as declare and log skeleton


    Gets the diagnostics dataframe from a log and the results
    of DCR-based conformance checking

    Parameters
    ---------------
    log
        Event log
    conf_result
        Results of conformance checking
    parameters
        Optional Parameter to specify case id key

    Returns
    ---------------
    diagn_dataframe
        Diagnostics dataframe
    """
    if parameters is None:
        parameters = {}

    case_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_CASEID_KEY, parameters, xes_constants.DEFAULT_TRACEID_KEY)
    import pandas as pd

    diagn_stream = []

    for index in range(len(log)):
        case_id = log[index].attributes[case_key]
        no_dev_total = conf_result[index]["no_dev_total"]
        no_constr_total = conf_result[index]["no_constr_total"]
        dev_fitness = conf_result[index]["dev_fitness"]

        diagn_stream.append({"case_id": case_id, "no_dev_total": no_dev_total, "no_constr_total": no_constr_total,
                             "dev_fitness": dev_fitness})

    return pd.DataFrame(diagn_stream)
