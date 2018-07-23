from lxml import etree
import pm4py.log.instance as log_instance
import pm4py.log.transform as log_transform
import pm4py.log.util.xes as xes_util

# defines correspondence between Python types and XES types
TYPE_CORRESPONDENCE = {
	"str":xes_util.TAG_STRING,
	"int":xes_util.TAG_INT,
	"float":xes_util.TAG_FLOAT,
	"datetime":xes_util.TAG_DATE
}
# if a type is not found in the previous list, then default to string
DEFAULT_TYPE = xes_util.TAG_STRING


def get_XES_attr_type(attrType):
	"""
	Transform a Python attribute type (e.g. str, datetime) into a XES attribute type (e.g. string, date)

	Parameters
	----------
	attrType
		Python attribute type
	"""
	if attrType in TYPE_CORRESPONDENCE:
		attrTypeXES = TYPE_CORRESPONDENCE[attrType]
	else:
		attrTypeXES = DEFAULT_TYPE
	return attrTypeXES

def get_XES_attr_value(attrValue, attrTypeXES):
	"""
	Transform an attribute value from Python format to XES format (the type is provided as argument)

	Parameters
	----------
	attrValue
		XES attribute value
	attrTypeXES
		XES attribute type

	"""
	if attrTypeXES == xes_util.TAG_DATE:
		defaultDateRepr = attrValue.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + attrValue.strftime('%z')[0:3] + ":" + attrValue.strftime('%z')[3:5]
		return defaultDateRepr.replace(" ","T")
	return str(attrValue)

def export_attributes(log, root):
	"""
	Export XES attributes (at the log level) from a PM4PY trace log

	Parameters
	----------
	log
		PM4PY trace log
	root
		Output XML root element

	"""
	for attr in log.attributes.keys():
		attrType = type(log.attributes[attr]).__name__
		attrTypeXES = get_XES_attr_type(attrType)
		attrValue = get_XES_attr_value(log.attributes[attr], attrTypeXES)
		if not attrTypeXES is None and not attr is None and not attrValue is None:
			logAttribute = etree.SubElement(root, attrTypeXES)
			logAttribute.set(xes_util.KEY_KEY,attr)
			logAttribute.set(xes_util.KEY_VALUE,attrValue)

def export_extensions(log, root):
	"""
	Export XES extensions from a PM4PY trace log

	Parameters
	----------
	log
		PM4PY trace log
	root
		Output XML root element

	"""
	for ext in log.extensions.keys():
		extValue = log.extensions[ext]
		logExtension = etree.SubElement(root, xes_util.TAG_EXTENSION)
		if not ext is None and not extValue[xes_util.KEY_PREFIX] is None and not extValue[xes_util.KEY_URI] is None:
			logExtension.set(xes_util.KEY_NAME, ext)
			logExtension.set(xes_util.KEY_PREFIX, extValue[xes_util.KEY_PREFIX])
			logExtension.set(xes_util.KEY_URI, extValue[xes_util.KEY_URI])

def export_globals(log, root):
	"""
	Export XES globals from a PM4PY trace log

	Parameters
	----------
	log
		PM4PY trace log
	root
		Output XML root element

	"""
	for glob in log.omni_present.keys():
		globEls = log.omni_present[glob]
		xesGlobal = etree.SubElement(root, xes_util.TAG_GLOBAL)
		for globEl in globEls.keys():
			globType = type(globEls[globEl]).__name__
			globTypeXES = get_XES_attr_type(globType)
			globValue = get_XES_attr_value(globEls[globEl], globTypeXES)
			if not globTypeXES is None and not globEl is None and not globValue is None:
				xesGlobalAttr = etree.SubElement(xesGlobal, globTypeXES)
				xesGlobalAttr.set(xes_util.KEY_KEY,globEl)
				xesGlobalAttr.set(xes_util.KEY_VALUE,globValue)

def export_classifiers(log, root):
	"""
	Export XES classifiers from a PM4PY trace log

	Parameters
	----------
	log
		PM4PY trace log
	root
		Output XML root element

	"""
	for clas in log.classifiers.keys():
		clasValue = log.classifiers[clas]
		classifier = etree.SubElement(root, xes_util.TAG_CLASSIFIER)
		classifier.set(xes_util.KEY_NAME, clas)
		classifier.set(xes_util.KEY_KEYS, " ".join(clasValue))

def export_traces_events(tr, trace):
	"""
	Export XES events given a PM4PY trace

	Parameters
	----------
	tr
		PM4PY trace
	trace
		Output XES trace

	"""
	for ev in tr:
		event = etree.SubElement(trace, xes_util.TAG_EVENT)
		
		for attr in ev:
			attrType = type(ev[attr]).__name__
			attrTypeXES = get_XES_attr_type(attrType)
			attrValue = get_XES_attr_value(ev[attr], attrTypeXES)
			
			eventAttribute = etree.SubElement(event, attrTypeXES)
			eventAttribute.set(xes_util.KEY_KEY,attr)
			eventAttribute.set(xes_util.KEY_VALUE,attrValue)

def export_traces(log, root):
	"""
	Export XES traces from a PM4PY trace log

	Parameters
	----------
	log
		PM4PY trace log
	root
		Output XML root element

	"""
	for tr in log:
		trace = etree.SubElement(root, xes_util.TAG_TRACE)
				
		for attr in tr.attributes.keys():
			attrType = type(tr.attributes[attr]).__name__
			attrTypeXES = get_XES_attr_type(attrType)
			attrValue = get_XES_attr_value(tr.attributes[attr], attrTypeXES)
			traceAttribute = etree.SubElement(trace, attrTypeXES)
			traceAttribute.set(xes_util.KEY_KEY,attr)
			traceAttribute.set(xes_util.KEY_VALUE,attrValue)
		
		export_traces_events(tr, trace)

def export_log(log, outputFilePath):
	"""
	Export XES log from a PM4PY trace log

	Parameters
	----------
	log
		PM4PY trace log
	outputFilePath
		Output file path

	"""
	
	# If the log is in log_instance.EventLog, then transform it into log_instance.TraceLog format
	if type(log) is log_instance.EventLog:
		log = log_transform.transform_event_log_to_trace_log(log)
	root = etree.Element(xes_util.TAG_LOG)
	
	# add attributes at the log level
	export_attributes(log, root)
	# add extensions at the log level
	export_extensions(log, root)
	# add globals at the log level
	export_globals(log, root)
	# add classifiers at the log level
	export_classifiers(log, root)
	# add traces at the log level
	export_traces(log, root)
	
	# Effectively do the export of the event log
	tree = etree.ElementTree(root)
	tree.write(outputFilePath, pretty_print=True, xml_declaration=True, encoding="utf-8")
