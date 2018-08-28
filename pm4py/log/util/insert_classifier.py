def search_and_insert_event_classifier_attribute(log):
    """
    Search among classifiers expressed in the log one that is good for the process model extraction

    Parameters
    -----------
    log
        Trace log

    Returns
    -----------
    log
        Trace log (plus eventually one additional event attribute as the classifier)
    classifier_attr_key
        Attribute name of the attribute that contains the classifier value
    """
    classifier = None
    if log.classifiers and "Activity classifier" in log.classifiers and log.classifiers["Activity classifier"]:
        classifier = "Activity classifier"
    elif log.classifiers and "MXML Legacy Classifier" in log.classifiers and log.classifiers["MXML Legacy Classifier"]:
        classifier = "MXML Legacy Classifier"
    return insert_classifier_attribute(log, classifier)

def insert_classifier_attribute(log, classifier):
    """
    Insert the specified classifier as additional event attribute in the log

    Parameters
    -----------
    log
        Trace log
    classifier
        Event classifier

    Returns
    --------
    log
        Trace log (plus eventually one additional event attribute as the classifier)
    classifier_attr_key
        Attribute name of the attribute that contains the classifier value
    """
    classifier_attr_key = None
    if classifier is not None:
        classifier_attr_key = "@@classifier"
        for trace in log:
            for event in trace:
                classifier_value = "+".join([event[x] for x in log.classifiers[classifier]])
                event[classifier_attr_key] = classifier_value
    return log, classifier_attr_key