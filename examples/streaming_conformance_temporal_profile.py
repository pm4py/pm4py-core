import pm4py
from pm4py.algo.discovery.temporal_profile import algorithm as temporal_profile_disc
from pm4py.streaming.algo.conformance.temporal import algorithm as streaming_temporal_conformance
from pm4py.streaming.stream.live_event_stream import LiveEventStream


def execute_script():
    log = pm4py.read_xes("../tests/input_data/receipt.xes")
    static_stream = pm4py.convert_to_event_stream(log)
    temporal_profile = temporal_profile_disc.apply(log)
    cc = streaming_temporal_conformance.apply(temporal_profile)
    live_stream = LiveEventStream()
    live_stream.register(cc)
    live_stream.start()
    for index, ev in enumerate(static_stream):
        live_stream.append(ev)
    live_stream.stop()
    print(cc.get())


if __name__ == "__main__":
    execute_script()
