from lxml import etree
from pm4py import log as log_lib
import ciso8601
import logging

# ITERPARSE EVENTS
EVENT_END = 'end'
EVENT_START = 'start'


def import_from_path_xes(path):
    context = etree.iterparse(path, events=['start', 'end'])

    log = None
    trace = None
    event = None

    tree = {}

    for tree_event, elem in context:

        if tree_event == EVENT_START:  # starting to read
            parent = tree[elem.getparent()] if elem.getparent() in tree else None

            if elem.tag.endswith(log_lib.util.xes.TAG_LOG):
                if log is not None:
                    raise SyntaxError('file contains > 1 <log> tags')
                log = log_lib.instance.TraceLog()
                tree[elem] = log.attributes

            elif elem.tag.endswith(log_lib.util.xes.TAG_TRACE):
                if trace is not None:
                    raise SyntaxError('file contains <trace> in another <trace> tag')
                trace = log_lib.instance.Trace()
                tree[elem] = trace.attributes

            elif elem.tag.endswith(log_lib.util.xes.TAG_EVENT):
                if event is not None:
                    raise SyntaxError('file contains <event> in another <event> tag')
                event = log_lib.instance.Event()
                tree[elem] = event

            elif elem.tag.endswith(log_lib.util.xes.TAG_EXTENSION):
                if log is None:
                    raise SyntaxError('extension found outside of <log> tag')
                if elem.get(log_lib.util.xes.KEY_NAME) is not None and elem.get(log_lib.util.xes.KEY_PREFIX) is not None and elem.get(log_lib.util.xes.KEY_URI) is not None:
                    log.extensions[elem.get(log_lib.util.xes.KEY_NAME)] = {log_lib.util.xes.KEY_PREFIX: elem.get(log_lib.util.xes.KEY_PREFIX),
                                                               log_lib.util.xes.KEY_URI: elem.get(log_lib.util.xes.KEY_URI)}

            elif elem.tag.endswith(log_lib.util.xes.TAG_GLOBAL):
                if log is None:
                    raise SyntaxError('global found outside of <log> tag')
                if elem.get(log_lib.util.xes.KEY_SCOPE) is not None:
                    log.omni_present[elem.get(log_lib.util.xes.KEY_SCOPE)] = {}
                    tree[elem] = log.omni_present[elem.get(log_lib.util.xes.KEY_SCOPE)]

            elif elem.tag.endswith(log_lib.util.xes.TAG_CLASSIFIER):
                if log is None:
                    raise SyntaxError('classifier found outside of <log> tag')
                if elem.get(log_lib.util.xes.KEY_KEYS) is not None:
                    log.classifiers[elem.get(log_lib.util.xes.KEY_NAME)] = elem.get(log_lib.util.xes.KEY_KEYS).split()

            elif elem.tag.endswith(log_lib.util.xes.TAG_DATE):
                try:
                    dt = ciso8601.parse_datetime(elem.get(log_lib.util.xes.KEY_VALUE))
                    tree = __parse_attribute(elem, parent, elem.get(log_lib.util.xes.KEY_KEY), dt, tree)
                except:
                    logging.info("failed to parse date: "+str(elem.get(log_lib.util.xes.KEY_VALUE)))

            elif elem.tag.endswith(log_lib.util.xes.TAG_STRING):
                if not parent is None:
                    tree = __parse_attribute(elem, parent, elem.get(log_lib.util.xes.KEY_KEY), elem.get(log_lib.util.xes.KEY_VALUE), tree)
            elif elem.tag.endswith(log_lib.util.xes.TAG_FLOAT):
                if not parent is None:
                    try:
                        val = float(elem.get(log_lib.util.xes.KEY_VALUE))
                        tree = __parse_attribute(elem, parent, elem.get(log_lib.util.xes.KEY_KEY), val, tree)
                    except:
                        logging.info("failed to parse float: "+str(elem.get(log_lib.util.xes.KEY_VALUE)))
            elif elem.tag.endswith(log_lib.util.xes.TAG_INT):
                if not parent is None:
                   try:
                       val = int(elem.get(log_lib.util.xes.KEY_VALUE))
                       tree = __parse_attribute(elem, parent, elem.get(log_lib.util.xes.KEY_KEY), val,tree)
                   except:
                       logging.info("failed to parse int: "+str(elem.get(log_lib.util.xes.KEY_VALUE)))
			
            elif elem.tag.endswith(log_lib.util.xes.TAG_BOOLEAN):
                if not parent is None:
                   try:
                       val = bool(elem.get(log_lib.util.xes.KEY_VALUE))
                       tree = __parse_attribute(elem, parent, elem.get(log_lib.util.xes.KEY_KEY), val, tree)
                   except:
                       logging.info("failed to parse boolean: "+str(elem.get(log_lib.util.xes.KEY_VALUE)))

            elif elem.tag.endswith(log_lib.util.xes.TAG_ID):
                if not parent is None:
                   tree = __parse_attribute(elem, parent, elem.get(log_lib.util.xes.KEY_KEY), elem.get(log_lib.util.xes.KEY_VALUE), tree)

            elif elem.tag.endswith(log_lib.util.xes.TAG_LIST):
                if not parent is None:
                   # lists have no value, hence we put None as a value
                   tree = __parse_attribute(elem, parent, elem.get(log_lib.util.xes.KEY_KEY), None, tree)

        elif tree_event == EVENT_END:
            if elem.tag.endswith(log_lib.util.xes.TAG_LOG):
                pass

            elif elem.tag.endswith(log_lib.util.xes.TAG_TRACE):
                log.append(trace)
                trace = None

            elif elem.tag.endswith(log_lib.util.xes.TAG_EVENT):
                if trace is not None:
                    trace.append(event)
                    event = None

            if elem in tree:
                del tree[elem]
            elem.clear()
            if elem.getprevious() is not None:
                try:
                    del elem.getparent()[0]
                except TypeError:
                    pass
    del context
    return log


def __parse_attribute(elem, store, key, value, tree):
    if len(elem.getchildren()) == 0:
        store[key] = value
    else:
        store[key] = {log_lib.util.xes.KEY_VALUE: value, log_lib.util.xes.KEY_CHILDREN: {}}
        if elem.getchildren()[0].tag.endswith(log_lib.util.xes.TAG_VALUES):
            tree[elem] = store[key][log_lib.util.xes.KEY_CHILDREN]
            tree[elem.getchildren()[0]] = tree[elem]
        else:
            tree[elem] = store[key][log_lib.util.xes.KEY_CHILDREN]
    return tree
