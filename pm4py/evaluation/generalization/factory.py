from pm4py.evaluation.generalization.versions import token_based

GENERALIZATION_TOKEN = "token_replay"
VERSIONS = {GENERALIZATION_TOKEN: token_based.apply}


def apply(log, petri_net, initial_marking, final_marking, parameters=None, variant="token_replay"):
    return VERSIONS[variant](log, petri_net, initial_marking, final_marking, parameters=parameters)
