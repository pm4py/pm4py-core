from pm4py.objects.conversion.dfg.versions import to_petri_net_activity_defines_place
import deprecation

VERSION_TO_PETRI_NET_ACTIVITY_DEFINES_PLACE = 'to_petri_net_activity_defines_place'

VERSIONS = {VERSION_TO_PETRI_NET_ACTIVITY_DEFINES_PLACE: to_petri_net_activity_defines_place.apply}

@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use algorithm entrypoint instead (conversion/dfg/factory)')
def apply(dfg, parameters=None, variant=VERSION_TO_PETRI_NET_ACTIVITY_DEFINES_PLACE):
    return VERSIONS[variant](dfg, parameters=parameters)
