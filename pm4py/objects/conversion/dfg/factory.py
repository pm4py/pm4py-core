from pm4py.objects.conversion.dfg.versions import to_petri_net_activity_defines_place


VERSION_TO_PETRI_NET_ACTIVITY_DEFINES_PLACE = 'to_petri_net_activity_defines_place'

VERSIONS = {VERSION_TO_PETRI_NET_ACTIVITY_DEFINES_PLACE: to_petri_net_activity_defines_place.apply}


def apply(dfg, parameters=None, variant=VERSION_TO_PETRI_NET_ACTIVITY_DEFINES_PLACE):
    return VERSIONS[variant](dfg, parameters=parameters)

