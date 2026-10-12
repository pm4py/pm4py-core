'''
PM4Py – A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see this software project's root or
visit <https://www.gnu.org/licenses/>.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
'''
if __name__ == "statistics":
    # Running Python from the pm4py directory can shadow the standard library.
    # Resolve top-level imports there without changing pm4py.statistics.
    import importlib.machinery
    import importlib.util
    import sys
    import sysconfig

    _spec = importlib.machinery.PathFinder.find_spec(
        __name__, [sysconfig.get_path("stdlib")]
    )
    if _spec is None or _spec.loader is None:
        raise ImportError("Cannot find the standard library statistics module")
    _stdlib_statistics = importlib.util.module_from_spec(_spec)
    sys.modules[__name__] = _stdlib_statistics
    _spec.loader.exec_module(_stdlib_statistics)
else:
    from pm4py.util import constants as pm4_constants

    if pm4_constants.ENABLE_INTERNAL_IMPORTS:
        from pm4py.statistics import (
            attributes,
            chaotic_activities,
            concurrent_activities,
            end_activities,
            eventually_follows,
            ocel,
            passed_time,
            process_cube,
            rework,
            service_time,
            sojourn_time,
            start_activities,
            traces,
            util,
            variants,
            overlap
        )
