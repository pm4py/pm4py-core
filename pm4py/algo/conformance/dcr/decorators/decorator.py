from abc import ABC, abstractmethod
from pm4py.algo.conformance.dcr.rules.condition import CheckCondition
from pm4py.algo.conformance.dcr.rules.exclude import CheckExclude
from pm4py.algo.conformance.dcr.rules.include import CheckInclude
from pm4py.algo.conformance.dcr.rules.response import CheckResponse


class Checker:
    """
        interface for checker and decorator
    """

    def enabled_checker(self, act, G, deviations, parameters=None) -> None:
        pass

    def all_checker(self, act, event, G, deviations, parameters=None) -> None:
        pass

    def accepting_checker(self, G, responses, deviations, parameters=None) -> None:
        pass


class ConcreteChecker(Checker):
    """
    base checker used for conformance checking of standard DCR graph, with the four relations:
        - Condition
        - Response
        - Include
        - Exclude
    """

    def enabled_checker(self, act, G, deviations, parameters=None) -> None:
        """
        Calls the methods used for checking deviation for a stand DCR graph

        Parameters
        ----------
        G
            DCR Graph
        act
            the activity that is executed
        deviations
            the list of deviations
        parameters
            optional parameters
        """
        CheckCondition.check_rule(act, G, deviations)
        CheckExclude.check_rule(act, G, deviations)
        CheckInclude.check_rule(act, G, deviations)

    def accepting_checker(self, G, responses, deviations, parameters=None) -> None:
        """
        Perform a check for rule that requires accepting state

        Parameters
        ----------
        G
            DCR Graph
        trace
            executed trace
        deviations
            the list of deviations
        parameters
            Optional, parameter containing keys used
        """
        CheckResponse.check_rule(G, responses, deviations)


class Decorator(Checker):
    def __init__(self, checker: Checker) -> None:
        self._checker = checker

    @property
    def checker(self) -> Checker:
        return self._checker

    def enabled_checker(self, act, G, deviations, parameters=None) -> None:
        self._checker.enabled_checker(act, G, deviations, parameters=parameters)

    def all_checker(self, act, event, G, deviations, parameters=None) -> None:
        self._checker.all_checker(act, event, G, deviations, parameters=parameters)

    def accepting_checker(self, G, trace, deviations, parameters=None) -> None:
        self._checker.accepting_checker(G, deviations, parameters=parameters)
