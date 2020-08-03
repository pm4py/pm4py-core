from pm4py.algo.discovery.footprints.outputs import Outputs

DFG = "dfg"
FOOTPRINTS_KEY = "footprints"
START_ACTIVITIES = "start_activities"
END_ACTIVITIES = "end_activities"
SEQUENCE = "sequence"
PARALLEL = "parallel"


def fp_fitness(fp_log, fp_model, conf_results, parameters=None):
    """
    Calculates the footprints fitness provided the footprints of the log,
    and the result of footprints conformance (applied to the entire log)

    Parameters
    ---------------
    fp_log
        Footprints of the log
    fp_model
        Footprints of the model
    conf_results
        Footprints conformance (applied to the entire log)
    parameters
        Parameters of the algorithm

    Returns
    ---------------
    fitness
        Fitness value (between 0.0 and 1.0)
    """
    if parameters is None:
        parameters = {}

    if type(conf_results) is list:
        raise Exception("method is working only on entire log footprints")
    elif type(conf_results) is dict:
        # extensive conformance variant
        footprints = conf_results[FOOTPRINTS_KEY]
    else:
        # normal conformance variant
        footprints = conf_results

    dfg = fp_log[DFG]
    num_sequence_log = len(fp_log[SEQUENCE])
    num_parallel_log = len(fp_log[PARALLEL])
    num_start_activities_log = len(fp_log[START_ACTIVITIES])
    num_end_activities_log = len(fp_log[END_ACTIVITIES])
    num_start_activities_dev = len(conf_results[START_ACTIVITIES])
    num_end_activities_dev = len(conf_results[END_ACTIVITIES])

    if dfg:
        sum_dfg = float(sum(x for x in dfg.values()))
        sum_dev = float(sum(dfg[x] for x in footprints))

        return ((1.0 - sum_dev / sum_dfg) * (num_sequence_log + num_parallel_log) + (
                    num_start_activities_log + num_end_activities_log - num_start_activities_dev - num_end_activities_dev)) / (
                           num_sequence_log + num_parallel_log + num_start_activities_log + num_end_activities_log)

    # return fitness 1.0 if DFG is empty
    return 1.0


def fp_precision(fp_log, fp_model, parameters=None):
    """
    Calculates the footprints based precision provided the two footprints
    of the log and the model.

    Parameters
    --------------
    fp_log
        Footprints of the log
    fp_model
        Footprints of the model
    parameters
        Parameters of the algorithm

    Returns
    -------------
    precision
        Precision value (between 0 and 1)
    """
    if parameters is None:
        parameters = {}

    log_configurations = fp_log[Outputs.SEQUENCE.value].union(fp_log[Outputs.PARALLEL.value])
    model_configurations = fp_model[Outputs.SEQUENCE.value].union(fp_model[Outputs.PARALLEL.value])

    if model_configurations:
        return float(len(log_configurations.intersection(model_configurations))) / float(len(model_configurations))

    # return precision 1.0 if model configurations are empty
    return 1.0
