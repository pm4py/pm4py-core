from pm4py.algo.conformance.dcr.decorators.decorator import Decorator
from pm4py.algo.conformance.dcr.rules.role import CheckRole
from pm4py.util import exec_utils, constants, xes_constants
from typing import Optional, Dict, Union, Any


class RoleDecorator(Decorator):
    def enabled_checker(self, *args, **kwargs):
        self._checker.enabled_checker(*args, **kwargs)

    def all_checker(self, act, event, model, deviations, parameters=None):
        self._checker.all_checker(act, event, model, deviations, parameters=parameters)
        resource_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_RESOURCE_KEY,parameters,xes_constants.DEFAULT_RESOURCE_KEY)
        role = event[resource_key]
        CheckRole.check_rule(act, model, role, deviations)