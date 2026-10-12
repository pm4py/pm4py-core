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
