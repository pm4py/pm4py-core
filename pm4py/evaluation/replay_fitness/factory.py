from pm4py.evaluation.replay_fitness.versions import alignment_based, token_replay

ALIGNMENT_BASED = "alignments"
TOKEN_BASED = "token_replay"
VERSIONS = {ALIGNMENT_BASED: alignment_based.apply, TOKEN_BASED: token_replay.apply}

PARAM_ACTIVITY_KEY = 'activity_key'

def apply(log, petri_net, initial_marking, final_marking, parameters=None, variant="token_replay"):
    return VERSIONS[variant](log, petri_net, initial_marking, final_marking, parameters=parameters)