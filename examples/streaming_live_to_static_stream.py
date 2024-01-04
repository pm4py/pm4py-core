from pm4py.streaming.importer.csv.variants import csv_event_stream
from pm4py.streaming.stream.live_event_stream import LiveEventStream
from pm4py.streaming.util.live_to_static_stream import LiveToStaticStream


def execute_script():
    # creates a live event stream, forwarding events to its algorithmic listeners
    live_stream = LiveEventStream()

    # in this case, the listener that we register to the live stream
    # just saves the list of events that are submitted to the live event stream
    static_stream_converter = LiveToStaticStream()
    live_stream.register(static_stream_converter)

    # starts the live event stream
    live_stream.start()
    # reads a CSV line-by-line and send its rows to the live event stream
    csv_reader = csv_event_stream.apply("../tests/input_data/running-example.csv")
    csv_reader.to_event_stream(live_stream)

    # stops the live event stream
    live_stream.stop()

    # gets the list of events stored inside the converter
    static_stream = static_stream_converter.get()
    print(static_stream)


if __name__ == "__main__":
    execute_script()
