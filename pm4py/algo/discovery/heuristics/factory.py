from pm4py.algo.discovery.heuristics.versions import classic

CLASSIC = "classic"

VERSIONS = {CLASSIC: classic.apply}
VERSIONS_PANDAS = {CLASSIC: classic.apply_pandas}
VERSIONS_DFG = {CLASSIC: classic.apply_dfg}
VERSIONS_HEU = {CLASSIC: classic.apply_heu}
VERSIONS_DFG_HEU = {CLASSIC: classic.apply_heu_dfg}


def apply(log, parameters=None, variant=CLASSIC):
    return VERSIONS[variant](log, parameters=parameters)


def apply_pandas(df, parameters=None, variant=CLASSIC):
    return VERSIONS_PANDAS[variant](df, parameters=parameters)


def apply_dfg(dfg, activities=None, activities_occurrences=None, start_activities=None, end_activities=None,
              parameters=None, variant=CLASSIC):
    return VERSIONS_DFG[variant](dfg, activities=activities, activities_occurrences=activities_occurrences,
                                 start_activities=start_activities, end_activities=end_activities,
                                 parameters=parameters)


def apply_heu(log, parameters=None, variant=CLASSIC):
    return VERSIONS_HEU[variant](log, parameters=parameters)


def apply_heu_dfg(dfg, activities=None, activities_occurrences=None, start_activities=None, end_activities=None,
                  parameters=None, variant=CLASSIC):
    return VERSIONS_DFG_HEU[variant](dfg, activities=activities, activities_occurrences=activities_occurrences,
                                     start_activities=start_activities, end_activities=end_activities,
                                     parameters=parameters)
