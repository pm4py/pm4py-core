from enum import Enum
from pm4py.algo.conformance.dcr.decorators.decorator import Decorator
from pm4py.algo.conformance.dcr.rules.role import CheckRole
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.objects.dcr.roles.obj import RoledcrGraph
from pm4py.objects.dcr.obj import DcrGraph
from typing import Optional, Dict, Union, Any, List, Tuple

class Parameters(Enum):
    GROUP_KEY = constants.PARAMETER_CONSTANT_GROUP_KEY

class RoleDecorator(Decorator):
    """
    The RoleDecorator Class is used to provide methods for checking deviations of roles.
    It will call a method to check if the current event is executed by an entity that has authority to perform
    the activity the event represents.

    Methods
    --------
    enabled_checker(event, graph, deviations, parameters=None)
        this method will call the underlying class used to check for deviations
    all_checker(event, event_attributes, graph, deviations, parameters=None)
        This method will determine if deviations occurs due to violation of role assignments
    enabled_checker(e, G, deviations, parameters=None)
        this method will call the underlying class used to check for deviations
    """
    def enabled_checker(self, event: str, graph: Union[RoledcrGraph, DcrGraph], deviations: List[Tuple[str, Any]], parameters: Optional[Dict[Union[str, Any], Any]] = None) -> None:
        self._checker.enabled_checker(event, graph, deviations, parameters)

    def all_checker(self, event: str, event_attributes: dict, graph: Union[RoledcrGraph, DcrGraph], deviations: List[Tuple[str, Any]], parameters: Optional[Dict[Union[str, Any], Any]] = None) -> None:
        self._checker.all_checker(event, event_attributes, graph, deviations, parameters=parameters)
        group_key = exec_utils.get_param_value(Parameters.GROUP_KEY,parameters,xes_constants.DEFAULT_GROUP_KEY)
        role = event_attributes[group_key]
        CheckRole.check_rule(event, graph, role, deviations)

    def accepting_checker(self, graph: Union[RoledcrGraph, DcrGraph], responses: List[Tuple[str, str]], deviations: List[Tuple[str, Any]], parameters: Optional[Dict[Union[str, Any], Any]] = None) -> None:
        self._checker.accepting_checker(graph, responses, deviations, parameters)