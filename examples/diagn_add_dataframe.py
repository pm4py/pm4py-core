import pm4py
from pm4py.algo.discovery.log_skeleton import algorithm as log_skeleton_discovery
from pm4py.algo.conformance.log_skeleton import algorithm as log_skeleton_conformance
from pm4py.util import constants, pandas_utils


def execute_script():
    # loads a XES event log
    event_log = pm4py.read_xes("../tests/input_data/receipt.xes")
    # gets the dataframe out of the event log (through conversion)
    dataframe = pm4py.convert_to_dataframe(event_log)
    # discovers the log skeleton model
    log_skeleton = log_skeleton_discovery.apply(event_log, parameters={log_skeleton_discovery.Variants.CLASSIC.value.Parameters.NOISE_THRESHOLD: 0.03})
    # apply conformance checking
    conf_result = log_skeleton_conformance.apply(event_log, log_skeleton)
    # gets the diagnostic result out of the dataframe
    diagnostics = log_skeleton_conformance.get_diagnostics_dataframe(event_log, conf_result)
    # merges the dataframe containing the events, and the diagnostics dataframe
    merged_df = pandas_utils.merge(dataframe, diagnostics, how="left", left_on="case:concept:name", right_on="case_id", suffixes=('', '_diagn'))
    print(merged_df)


if __name__ == "__main__":
    execute_script()
