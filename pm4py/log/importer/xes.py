from lxml import etree
import pm4py.log.instance as log_instance
import pm4py.log.util.xes as xes_util
import ciso8601

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

            if elem.tag.endswith(xes_util.TAG_LOG):
                if log is not None:
                    raise SyntaxError('file contains > 1 <log> tags')
                log = log_instance.TraceLog()
                tree[elem] = log.attributes

            elif elem.tag.endswith(xes_util.TAG_TRACE):
                if trace is not None:
                    raise SyntaxError('file contains <trace> in another <trace> tag')
                trace = log_instance.Trace()
                tree[elem] = trace.attributes

            elif elem.tag.endswith(xes_util.TAG_EVENT):
                if event is not None:
                    raise SyntaxError('file contains <event> in another <event> tag')
                event = log_instance.Event()
                tree[elem] = event

            elif elem.tag.endswith(xes_util.TAG_EXTENSION):
                if log is None:
                    raise SyntaxError('extension found outside of <log> tag')
                log.extensions[elem.get(xes_util.KEY_NAME)] = {xes_util.KEY_PREFIX: elem.get(xes_util.KEY_PREFIX),
                                                               xes_util.KEY_URI: elem.get(xes_util.KEY_URI)}

            elif elem.tag.endswith(xes_util.TAG_GLOBAL):
                if log is None:
                    raise SyntaxError('global found outside of <log> tag')
                log.omni_present[elem.get(xes_util.KEY_SCOPE)] = {}
                tree[elem] = log.omni_present[elem.get(xes_util.KEY_SCOPE)]

            elif elem.tag.endswith(xes_util.TAG_CLASSIFIER):
                if log is None:
                    raise SyntaxError('classifier found outside of <log> tag')
                log.classifiers[elem.get(xes_util.KEY_NAME)] = elem.get(xes_util.KEY_KEYS).split()

            elif elem.tag.endswith(xes_util.TAG_DATE):
                dt = ciso8601.parse_datetime(elem.get(xes_util.KEY_VALUE))
                tree = __parse_attribute(elem, parent, elem.get(xes_util.KEY_KEY), dt, tree)

            elif elem.tag.endswith(xes_util.TAG_STRING):
                tree = __parse_attribute(elem, parent, elem.get(xes_util.KEY_KEY), elem.get(xes_util.KEY_VALUE), tree)

            elif elem.tag.endswith(xes_util.TAG_FLOAT):
                tree = __parse_attribute(elem, parent, elem.get(xes_util.KEY_KEY), float(elem.get(xes_util.KEY_VALUE)),
                                         tree)

            elif elem.tag.endswith(xes_util.TAG_INT):
                tree = __parse_attribute(elem, parent, elem.get(xes_util.KEY_KEY), int(elem.get(xes_util.KEY_VALUE)),
                                         tree)

            elif elem.tag.endswith(xes_util.TAG_BOOLEAN):
                tree = __parse_attribute(elem, parent, elem.get(xes_util.KEY_KEY), bool(elem.get(xes_util.KEY_VALUE)),
                                         tree)

            elif elem.tag.endswith(xes_util.TAG_ID):
                tree = __parse_attribute(elem, parent, elem.get(xes_util.KEY_KEY), elem.get(xes_util.KEY_VALUE), tree)

            elif elem.tag.endswith(xes_util.TAG_LIST):
                # lists have no value, hence we put None as a value
                tree = __parse_attribute(elem, parent, elem.get(xes_util.KEY_KEY), None, tree)

        elif tree_event == EVENT_END:
            if elem.tag.endswith(xes_util.TAG_LOG):
                pass

            elif elem.tag.endswith(xes_util.TAG_TRACE):
                log.append(trace)
                trace = None

            elif elem.tag.endswith(xes_util.TAG_EVENT):
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
        store[key] = {xes_util.KEY_VALUE: value, xes_util.KEY_CHILDREN: {}}
        tree[elem] = store[elem.get(xes_util.KEY_KEY)][xes_util.KEY_CHILDREN]
    return tree
