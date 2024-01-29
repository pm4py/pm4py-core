from pm4py.streaming.stream.live_event_stream import LiveEventStream
from pm4py.streaming.connectors.windows.click_key_logger import WindowsEventLogger
from pm4py.streaming.util.event_stream_printer import EventStreamPrinter
import time


def execute_script():
    stream = LiveEventStream()
    wel = WindowsEventLogger(stream, screenshots_folder="output")
    printer = EventStreamPrinter()
    stream.register(printer)
    stream.start()
    wel.start()

    print("listening")

    # listen only for 5 seconds
    time.sleep(5)

    wel.stop()
    stream.stop()

    print("stopped")


if __name__ == "__main__":
    execute_script()
