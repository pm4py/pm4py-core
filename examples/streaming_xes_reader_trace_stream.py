from pm4py.streaming.stream.live_trace_stream import LiveTraceStream
from pm4py.streaming.importer.xes import importer as streaming_xes_importer
from pm4py.streaming.util.trace_stream_printer import TraceStreamPrinter
import os, time


def execute_script():
    live_trace_stream = LiveTraceStream()
    trace_stream_printer = TraceStreamPrinter()
    live_trace_stream.register(trace_stream_printer)
    live_trace_stream.start()
    importer = streaming_xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"),
                                            variant=streaming_xes_importer.Variants.XES_TRACE_STREAM)
    importer.to_trace_stream(live_trace_stream)
    live_trace_stream.stop()


if __name__ == "__main__":
    execute_script()
