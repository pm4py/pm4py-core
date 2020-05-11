import unittest

from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.conversion.log import factory as log_conv_factory

import os


class SerializationTest(unittest.TestCase):
    def test_serialization_log(self):
        from pm4py.objects.log.serialization import factory as serialization_factory
        from pm4py.objects.log.deserialization import factory as deserialization_factory
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        ser = serialization_factory.apply(log)
        deser = deserialization_factory.apply(ser, variant="pyarrow_event_log")

    def test_serialization_stream(self):
        from pm4py.objects.log.serialization import factory as serialization_factory
        from pm4py.objects.log.deserialization import factory as deserialization_factory
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        stream = log_conv_factory.apply(log, variant=log_conv_factory.TO_EVENT_STREAM)
        ser = serialization_factory.apply(stream)
        deser = deserialization_factory.apply(ser, variant="pyarrow_event_stream")


if __name__ == "__main__":
    unittest.main()
