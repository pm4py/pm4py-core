from pm4py.evaluation.replay_fitness.versions import alignment_based

ALIGNMENT_BASED = "alignments"
VERSIONS = {ALIGNMENT_BASED: alignment_based.apply}

PARAM_ACTIVITY_KEY = 'activity_key'

def apply(log, petri_net, initial_marking, final_marking, parameters=None, variant="alignments"):
    return VERSIONS[ALIGNMENT_BASED](log, petri_net, initial_marking, final_marking, parameters=parameters)