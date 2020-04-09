import unittest

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.conversion.log import factory as log_conversion

import os


class SerializationTest(unittest.TestCase):
    def test_serialization_log(self):
        from pm4py.objects.log.serialization import algorithm as serialization
        from pm4py.objects.log.deserialization import algorithm as deserialization
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        ser = serialization.apply(log)
        deser = deserialization.apply(ser, variant="pyarrow_event_log")

    def test_serialization_stream(self):
        from pm4py.objects.log.serialization import algorithm as serialization
        from pm4py.objects.log.deserialization import algorithm as deserialization
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        stream = log_conversion.apply(log, variant=log_conversion.TO_EVENT_STREAM)
        ser = serialization.apply(stream)
        deser = deserialization.apply(ser, variant="pyarrow_event_stream")


if __name__ == "__main__":
    unittest.main()
