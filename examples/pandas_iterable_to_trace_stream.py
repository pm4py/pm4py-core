import pandas as pd
import pm4py
import os
from pm4py.streaming.conversion import from_pandas
from pm4py.streaming.stream.live_trace_stream import LiveTraceStream
from pm4py.streaming.util import trace_stream_printer


def execute_script():
    df = pd.read_csv(os.path.join("..", "tests", "input_data", "receipt.csv"))
    df = pm4py.format_dataframe(df)
    it = from_pandas.apply(df)
    printer = trace_stream_printer.TraceStreamPrinter()
    trace_stream = LiveTraceStream()
    trace_stream.register(printer)
    trace_stream.start()
    it.to_trace_stream(trace_stream)
    trace_stream.stop()


if __name__ == "__main__":
    execute_script()
