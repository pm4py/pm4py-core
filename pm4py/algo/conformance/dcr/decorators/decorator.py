from abc import ABC, abstractmethod
from pm4py.algo.conformance.dcr.rules.condition import CheckCondition
from pm4py.algo.conformance.dcr.rules.exclude import CheckExclude
from pm4py.algo.conformance.dcr.rules.include import CheckInclude
from pm4py.algo.conformance.dcr.rules.response import CheckResponse
from pm4py.objects.dcr.obj import DCR_Graph
from typing import List, Any, Dict, Tuple, Optional, Union

class Checker(ABC):
    """
    The checker class provides the methods that must be inherited by the decorators.
    The checker class instantiates the conformance checker methods that will be overwritten to perform the determine possible deviations.
    currently supports:
        * For the standard base DCR graph, enabled_checker() and accepting_checker() methods are used
        * For a DCR Graph with roles, the all_checker() methods was derived to give a means for checking deviating role assignment

    Methods
    --------
    enabled_Checker(act, G, deviations, parameters):
        method to determine deviations of non enabled events, i.e events that are not allowed to execute
    all_checker(act, event, G, deviations, parameters):
        method to determine deviations of event for each execution
    accepting_checker(G, responses, deviations, parameters):
        method to determine deviations that caused DCR graph to be in a non-accepting state.
    """

    @abstractmethod
    def enabled_checker(self, e: str, G: DCR_Graph, deviations:List[Tuple[str, Any]], parameters: Optional[Dict[Union[str, Any], Any]] = None) -> None:
        pass

    @abstractmethod
    def all_checker(self, e: str, event: dict, G: DCR_Graph, deviations:List[Tuple[str, Any]], parameters: Optional[Dict[Union[str, Any], Any]] = None) -> None:
        pass

    @abstractmethod
    def accepting_checker(self, G: DCR_Graph, responses:List[Tuple[str, str]], deviations, parameters: Optional[Dict[Union[str, Any], Any]] = None) -> None:
        pass


class ConcreteChecker(Checker):
    """
    The ConcreteChecker class, provides the base for the functionality that the checker should provide.

    Contains all the methods needed to perform conformance checking for a base DCR Graph

    Methods
    --------
    enabled_Checker(act, G, deviations, parameters):
        Determine the deviation that caused it not to be enabled
    all_checker(act, event, G, deviations, parameters):
        Checks for nothing as no rule for a base DCR graph has rules that would be required to determine with every execution of an event
    accepting_checker(G, responses, deviations, parameters):
        determine the deviation that caused the DCR graph to be non-accepting after an execution of a trace
    """

    def enabled_checker(self, e: str, G: DCR_Graph, deviations: List[Tuple[str, Any]], parameters: Optional[Dict[Union[str, Any], Any]] = None) -> None:
        """
        enabled_checker() is called when an event that is to be executed is not enabled
        Check all the deviations that could be associated with a not enabled event for a base DCR Graph

        Parameters
        ----------
        e: str
            the executed event
        G: DCR_Graph
            DCR Graph
        deviations:
            the list of deviations
        parameters
            optional parameters
        """
        CheckCondition.check_rule(e, G, deviations)
        CheckExclude.check_rule(e, G, deviations)
        CheckInclude.check_rule(e, G, deviations)

    def all_checker(self, e: str, event: dict, G: DCR_Graph, deviations: List[Tuple[str, Any]], parameters: Optional[Dict[Union[str, Any], Any]] = None) -> None:
        pass

    def accepting_checker(self, G: DCR_Graph, responses: List[Tuple[str, str]], deviations: List[Tuple[str, Any]], parameters: Optional[Dict[Union[str, Any], Any]] = None) -> None:
        """
        accepting_checker is called when a DCR graph is not accepting after an execution of a trace
        checks all response deviations for a base DCR Graph

        Parameters
        ----------
        G: DCR_Graph
            DCR Graph
        responses: List[Tuple[str, str]]
            list of response constraint not fulfilled
        deviations: List[Tuple[str, Any]]
            the list of deviations
        parameters: Optional[Dict[Union[str, Any], Any]]
            Optional, parameter containing keys used
        """
        CheckResponse.check_rule(G, responses, deviations)


class Decorator(Checker):
    """
    The Decorator class inherits the function that should be decorated from the Checker class.

    This class will instantiate with the checker as an attribute,
    that then can call the underlying the established methods from the underlying class

    Attributes
    ----------
    checker: Checker
        The checker that will be decorated

    Methods
    -------
    enabled_checker(e, G, deviations, parameters=None)
        calls the underlying enabled_checker
    enabled_checker(e, event, G, deviations, parameters=None)
        calls the underlying all_checker
    accepting_checker(G, responses, deviations, parameters=None)
        calls the underlying accepting_checker
    """

    def __init__(self, checker: Checker) -> None:
        """
        Constructs the checker with another checker, such that it can be called

        Parameters
        ----------
        checker: Checker
            The checker that will be decorated
        """
        self._checker = checker

    def enabled_checker(self, e: str, G: DCR_Graph, deviations: List[Tuple[str, Any]], parameters: Optional[Dict[Union[str, Any], Any]] = None) -> None:
        """
        This method calls enabled_checker() of the underlying class to continue search for cause of deviation between Graph and event Log

        Parameters
        ----------
        e: str
            Current event ID in trace
        G: DCR_Graph
            DCR Graph
        deviations: List[Tuple[str, Any]]
            List of deviations
        parameters: Optional[Dict[Union[str, Any], Any]]
            optional parameters
        """
        self._checker.enabled_checker(e, G, deviations, parameters=parameters)

    def all_checker(self, e: str, event: dict, G: DCR_Graph, deviations: List[Tuple[str, Any]], parameters: Optional[Dict[Union[str, Any], Any]] = None) -> None:
        """
        This method calls all_checker() of the underlying class to continue search for cause of deviation between Graph and event Log

        Parameters
        ----------
        e: str
            Current event ID in trace
        event: dict
            Current event with all attributes
        G: DCR_Graph
            DCR Graph
        deviations: List[Tuple[str, Any]]
            List of deviations
        parameters: Optional[Dict[Union[str, Any], Any]]
            optional parameters
        """
        self._checker.all_checker(e, event, G, deviations, parameters=parameters)

    def accepting_checker(self, G: DCR_Graph, responses: List[Tuple[str, str]], deviations: List[Tuple[str, Any]], parameters: Optional[Dict[Union[str, Any], Any]] = None) -> None:
        """
        This method calls accepting_checker() of the underlying class to continue search for cause of deviation between Graph and event Log

        Parameters
        ----------
        G: DCR_Graph
            DCR Graph
        responses: List[Tuple[str, str]]
            The recorded response relation between events to be executed and it originator
        deviations: List[Tuple[str, Any]]
            List of deviations
        parameters: Optional[Dict[Union[str, Any], Any]]
            optional parameters
        """
        self._checker.accepting_checker(G, responses, deviations, parameters=parameters)
