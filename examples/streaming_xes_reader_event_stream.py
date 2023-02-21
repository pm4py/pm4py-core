from pm4py.streaming.stream.live_event_stream import LiveEventStream
from pm4py.streaming.importer.xes import importer as streaming_xes_importer
from pm4py.streaming.util.event_stream_printer import EventStreamPrinter
import os, time


def execute_script():
    live_event_stream = LiveEventStream()
    event_stream_printer = EventStreamPrinter()
    live_event_stream.register(event_stream_printer)
    live_event_stream.start()
    importer = streaming_xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"),
                                            variant=streaming_xes_importer.Variants.XES_EVENT_STREAM)
    importer.to_event_stream(live_event_stream)
    live_event_stream.stop()


if __name__ == "__main__":
    execute_script()
