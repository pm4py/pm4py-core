from pm4py.objects.log.importer import csv, xes
try:
    # Python 3.8 or Win32 compatibility
    from pm4py.objects.log.importer import parquet
except:
    pass
