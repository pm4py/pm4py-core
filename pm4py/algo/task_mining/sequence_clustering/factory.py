from pm4py.algo.task_mining.sequence_clustering.versions import asyn_fluidc

ASYN_FLUIDC = "asyn_fluidc"

VERSIONS = {ASYN_FLUIDC: asyn_fluidc.apply}


def apply(frequents_label, frequents_encodings, variant=ASYN_FLUIDC, parameters=None):
    """
    Apply a clustering algorithm on the encodings

    Parameters
    ---------------
    frequents_label
        Label of the sequences
    frequents_encodings
        Encodings of the sequences
    variant
        Variant of the algorithm to apply, possible values: asyn_fluidc
    parameters
        Parameters of the algorithm

    Returns
    ----------------
    communities
        Communities
    """
    return VERSIONS[variant](frequents_label, frequents_encodings, parameters=parameters)
