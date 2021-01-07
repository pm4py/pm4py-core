import os

import pm4py
from pm4py.streaming.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.streaming.stream.live_event_stream import LiveEventStream
from pm4py.visualization.dfg import visualizer as dfg_visualizer


def execute_script():
    # imports a XES event log
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))
    # converts the log into a list of events (not anymore grouped in cases)
    event_stream = pm4py.convert_to_event_stream(log)
    # creates a live event stream (an object that distributes the messages to the algorithm)
    live_stream = LiveEventStream()
    # creates the streaming DFG discovery object
    stream_dfg_disc = dfg_discovery.apply()
    # register the discovery algorithm to the stream
    live_stream.register(stream_dfg_disc)
    # start the recording of events from the live event stream
    live_stream.start()
    # append each event of the original log to the live event stream
    # (so it is sent to the conformance checking algorithm)
    for event in event_stream:
        live_stream.append(event)
    # stops the live event stream
    live_stream.stop()
    # gets the DFG along with the start and end activities from the stream
    dfg, activities, start_activities, end_activities = stream_dfg_disc.get()
    # visualize the DFG
    gviz = dfg_visualizer.apply(dfg, variant=dfg_visualizer.Variants.FREQUENCY, activities_count=activities,
                                parameters={"format": "svg", "start_activities": start_activities,
                                            "end_activities": end_activities})
    dfg_visualizer.view(gviz)


if __name__ == "__main__":
    execute_script()
