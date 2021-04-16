import pm4py
from pm4py.algo.discovery.footprints import algorithm as fp_discovery
from pm4py.streaming.stream.live_event_stream import LiveEventStream
from pm4py.streaming.algo.conformance.footprints import algorithm as streaming_fp_conf
import os, time


def execute_script():
    # imports a XES event log
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))
    # converts the log into a list of events (not anymore grouped in cases)
    event_stream = pm4py.convert_to_event_stream(log)
    # calculates a process tree using the IMf algorithm (50% noise)
    tree = pm4py.discover_process_tree_inductive(log, noise_threshold=0.5)
    # discovers the footprint matrix from the process tree
    footprints = fp_discovery.apply(tree)
    # creates a live event stream (an object that distributes the messages to the algorithm)
    live_stream = LiveEventStream()
    # creates the TBR streaming conformance checking object
    conf_obj = streaming_fp_conf.apply(footprints)
    # register the conformance checking object to the live event stream
    live_stream.register(conf_obj)
    # start the recording of events from the live event stream
    live_stream.start()
    # append each event of the original log to the live event stream
    # (so it is sent to the conformance checking algorithm)
    for index, event in enumerate(event_stream):
        live_stream.append(event)
    # stops the live event stream
    live_stream.stop()
    # sends a termination signal to the conformance checking algorithm;
    # the conditions on the closure of all the cases are checked
    # (for each case, it is checked whether the end activity of the case
    # is possible according to the footprints)
    diagn_df = conf_obj.get()
    conf_obj.terminate_all()
    print(diagn_df)
    print(diagn_df[diagn_df["is_fit"] == False])


if __name__ == "__main__":
    execute_script()
