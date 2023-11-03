from abc import ABC, abstractmethod
from pm4py.algo.conformance.dcr.rules.condition import CheckCondition
from pm4py.algo.conformance.dcr.rules.exclude import CheckExclude
from pm4py.algo.conformance.dcr.rules.include import CheckInclude
from pm4py.algo.conformance.dcr.rules.response import CheckResponse


class Checker():
    """
        The base Component interface defines operations that can be altered by
        decorators.
    """

    def enabled_checker(self, act, G, deviations, parameters=None) -> None:
        pass

    def all_checker(self, act, event, G, deviations, parameters=None) -> None:
        pass

    def accepting_checker(self, G, deviations, parameters=None) -> None:
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
        act
            the activity that is performed
        model
            the DCR graph
        deviations
            the list of deviations already found
        parameters
            optional parameters
        """
        CheckCondition.check_rule(act, G, deviations)
        CheckExclude.check_rule(act, G, deviations)
        CheckInclude.check_rule(act, G, deviations)

    def accepting_checker(self, G, deviations, parameters=None) -> None:
        """
        Perform a check for rule that requires accepting state

        Parameters
        ----------
        model

        deviations
            List of deviations in log
        parameters
            Optional, parameter containing keys used
        """
        CheckResponse.check_rule(G, deviations)


class Decorator(Checker):
    def __init__(self, checker: Checker) -> None:
        self._checker = checker

    @property
    def checker(self) -> Checker:
        return self._checker

    def enabled_checker(self, act, G, deviations, parameters=None) -> None:
        self._checker.enabled_checker(act, G, deviations, parameters=parameters)

    def all_checker(self, act, event, G, deviations, parameters=None):
        self._checker.all_checker(act, event, G, deviations, parameters=parameters)

    def accepting_checker(self, G, deviations, parameters=None) -> None:
        self._checker.accepting_checker(G, deviations, parameters=parameters)
