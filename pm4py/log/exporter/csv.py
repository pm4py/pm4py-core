from lxml import etree
import pm4py.log.instance as log_instance
import pm4py.log.transform as log_transform
import pandas as pd

def export_log(log, outputFilePath):
	"""
	Exports the given log to csv format

	Parameters
	----------
	log: :class:`pm4py.log.instance.EventLog`
		Event log. Also, can take a trace log and convert it to event log
	outputFilePath:
		Output file path
	"""
	if type(log) is log_instance.TraceLog:
		log = log_transform.transform_trace_log_to_event_log(log)
	transfLog = [dict(x) for x in log]
	df = pd.DataFrame.from_dict(transfLog)
	df.to_csv(outputFilePath)