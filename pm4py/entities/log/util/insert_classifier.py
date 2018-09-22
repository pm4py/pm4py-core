def search_and_insert_event_classifier_attribute(log, force_activity_transition_insertion=False):
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
    force_activity_transition_insertion
        Optionally force the activitiy+transition classifier insertion
    """
    classifier = None
    if log.classifiers and "Activity classifier" in log.classifiers and log.classifiers["Activity classifier"]:
        classifier = "Activity classifier"
    elif log.classifiers and "MXML Legacy Classifier" in log.classifiers and log.classifiers["MXML Legacy Classifier"]:
        classifier = "MXML Legacy Classifier"
    return insert_classifier_attribute(log, classifier, force_activity_transition_insertion=force_activity_transition_insertion)

def insert_classifier_attribute(log, classifier, force_activity_transition_insertion=False):
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
    force_activity_transition_insertion
        Optionally force the activitiy+transition classifier insertion
    """
    classifier_attr_key = None
    if classifier is not None:
        classifier_attr_key = "@@classifier"
        for trace in log:
            for event in trace:
                classifier_value = "+".join([event[x] for x in log.classifiers[classifier]])
                event[classifier_attr_key] = classifier_value
    elif force_activity_transition_insertion:
        if len(log) > 0 and len(log[0]) > 0 and "concept:name" in log[0][0] and "lifecycle:transition" in log[0][0]:
            classifier_attr_key = "@@classifier"
            for trace in log:
                for event in trace:
                    classifier_value = event["concept:name"] + "+" + event["lifecycle:transition"]
                    event[classifier_attr_key] = classifier_value
    return log, classifier_attr_key