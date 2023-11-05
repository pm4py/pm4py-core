from pm4py.algo.conformance.dcr.decorators.decorator import Decorator
from pm4py.algo.conformance.dcr.rules.role import CheckRole
from pm4py.util import exec_utils, constants, xes_constants
from typing import Optional, Dict, Union, Any


class RoleDecorator(Decorator):
    def enabled_checker(self, *args, **kwargs):
        self._checker.enabled_checker(*args, **kwargs)

    def all_checker(self, act, event, model, deviations, parameters=None):
        self._checker.all_checker(act, event, model, deviations, parameters=parameters)
        group_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_GROUP_KEY,parameters,xes_constants.DEFAULT_GROUP_KEY)
        role = event[group_key]
        CheckRole.check_rule(act, model, role, deviations)