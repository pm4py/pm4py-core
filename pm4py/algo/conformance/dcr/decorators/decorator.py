from abc import ABC, abstractmethod
from pm4py.algo.conformance.dcr.rules.condition import CheckCondition
from pm4py.algo.conformance.dcr.rules.exclude import CheckExclude
from pm4py.algo.conformance.dcr.rules.include import CheckInclude
from pm4py.algo.conformance.dcr.rules.response import CheckResponse
from pm4py.objects.dcr.obj import DcrGraph
from typing import List, Any, Dict, Tuple, Optional, Union

class Checker(ABC):
    """
    An interface for Checker implementations and related decorators.

    This abstract base class defines the fundamental checker methods that must be implemented by concrete
    checker classes. These methods are aimed at evaluating various conformance rules within a DCR graph.

    Methods
    -------
    enabled_checker(act, G, deviations, parameters=None):
        Abstract method to check rules when an activity is enabled.

    all_checker(act, event, G, deviations, parameters=None):
        Abstract method to check rules for all types of activities.

    accepting_checker(G, responses, deviations, parameters=None):
        Abstract method to check for rules requiring an accepting state.
    The checker class provides the methods that must be inherited by the decorators.
    The checker class instantiates the conformance checker methods that will be overwritten to perform the determine possible deviations.
    currently supports:
        * For the standard base DCR graph, enabled_checker() and accepting_checker() methods are used
        * For a DCR Graph with roles, the all_checker() methods was derived to give a means for checking deviating role assignment

    Methods
    --------
    enabled_Checker(event, graph, deviations, parameters):
        method to determine deviations of non enabled events, i.e events that are not allowed to execute
    all_checker(event, event_attributes, graph, deviations, parameters):
        method to determine deviations of event for each execution
    accepting_checker(graph, responses, deviations, parameters):
        method to determine deviations that caused DCR graph to be in a non-accepting state.
    """

    @abstractmethod
    def enabled_checker(self, event: str, graph: DcrGraph, deviations:List[Any], parameters: Optional[Dict[Union[str, Any], Any]] = None) -> None:
        pass

    @abstractmethod
    def all_checker(self, event: str, event_attributes: dict, graph: DcrGraph, deviations:List[Any], parameters: Optional[Dict[Union[str, Any], Any]] = None) -> None:
        pass

    @abstractmethod
    def accepting_checker(self, graph: DcrGraph, responses: List[Tuple[str, str]], deviations:List[Any], parameters: Optional[Dict[Union[str, Any], Any]] = None) -> None:
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

    def enabled_checker(self, event: str, graph: DcrGraph, deviations: List[Any], parameters: Optional[Dict[Union[str, Any], Any]] = None) -> None:
        """
        enabled_checker() is called when an event that is to be executed is not enabled
        Check all the deviations that could be associated with a not enabled event for a base DCR Graph

        Parameters
        ----------
        event: str
            the executed event
        graph: DcrGraph
            DCR Graph
        deviations: List[Any]
            the list of deviations
        parameters: Optional[Dict[Union[str, Any], Any]]
            optional parameters
        """
        CheckCondition.check_rule(event, graph, deviations)
        CheckExclude.check_rule(event, graph, parameters['executionHistory'], deviations)
        CheckInclude.check_rule(event, graph, deviations)

    def all_checker(self, event: str, event_attributes: dict, graph: DcrGraph, deviations: List[Any], parameters: Optional[Dict[Union[str, Any], Any]] = None) -> None:
        pass

    def accepting_checker(self, graph: DcrGraph, responses: List[Tuple[str, str]], deviations: List[Any], parameters: Optional[Dict[Union[str, Any], Any]] = None) -> None:
        """
        accepting_checker is called when a DCR graph is not accepting after an execution of a trace
        checks all response deviations for a base DCR Graph

        Parameters
        ----------
        graph: DcrGraph
            DCR Graph
        responses: List[Tuple[str, str]]
            list of response constraint not fulfilled
        deviations: List[Any]
            the list of deviations
        parameters: Optional[Dict[Union[str, Any], Any]]
            Optional, parameter containing keys used
        """
        CheckResponse.check_rule(graph, responses, deviations)


class Decorator(Checker):
    """
    A decorator for Checker objects, providing a flexible mechanism to enhance or modify their behavior.

    This class implements the decorator pattern to wrap a Checker object. It overrides the Checker
    interface methods and can add additional functionality before or after invoking these methods on
    the wrapped Checker instance.

    Inherits From
    --------------
    Checker : The abstract base class for checker implementations.

    Attributes
    ----------

    self._checker : Checker
        The internal Checker instance that is being decorated.

    Methods
    -------
    enabled_checker(act, G, deviations, parameters=None):
        Invokes the enabled_checker method on the decorated Checker instance, potentially adding extra behavior.

    all_checker(act, event, G, deviations, parameters=None):
        Invokes the all_checker method on the decorated Checker instance, potentially adding extra behavior.

    accepting_checker(G, trace, deviations, parameters=None):
        Invokes the accepting_checker method on the decorated Checker instance, potentially adding extra behavior.
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

    def enabled_checker(self, event: str, graph: DcrGraph, deviations: List[Any], parameters: Optional[Dict[Union[str, Any], Any]] = None) -> None:
        """
        This method calls enabled_checker() of the underlying class to continue search for cause of deviation between Graph and event Log

        Parameters
        ----------
        event: str
            Current event ID in trace
        graph: DcrGraph
            DCR Graph
        deviations: List[Any]
            List of deviations
        parameters: Optional[Dict[Union[str, Any], Any]]
            optional parameters
        """
        self._checker.enabled_checker(event, graph, deviations, parameters=parameters)

    def all_checker(self, event: str, event_attributes: dict, graph: DcrGraph, deviations: List[Any], parameters: Optional[Dict[Union[str, Any], Any]] = None) -> None:
        """
        This method calls all_checker() of the underlying class to continue search for cause of deviation between Graph and event Log

        Parameters
        ----------
        event: str
            Current event ID in trace
        event_attributes: dict
            Current event with all attributes
        graph: DcrGraph
            DCR Graph
        deviations: List[Any]
            List of deviations
        parameters: Optional[Dict[Union[str, Any], Any]]
            optional parameters
        """
        self._checker.all_checker(event, event_attributes, graph, deviations, parameters=parameters)

    def accepting_checker(self, graph: DcrGraph, responses: List[Tuple[str, str]], deviations: List[Any], parameters: Optional[Dict[Union[str, Any], Any]] = None) -> None:
        """
        This method calls accepting_checker() of the underlying class to continue search for cause of deviation between Graph and event Log

        Parameters
        ----------
        graph: DcrGraph
            DCR Graph
        responses: List[Tuple[str, str]]
            The recorded response relation between events to be executed and it originator
        deviations: List[Any]
            List of deviations
        parameters: Optional[Dict[Union[str, Any], Any]]
            optional parameters
        """
        self._checker.accepting_checker(graph, responses, deviations, parameters=parameters)
