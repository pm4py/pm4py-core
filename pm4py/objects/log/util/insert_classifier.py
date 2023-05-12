'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
def search_act_class_attr(log, force_activity_transition_insertion=False):
    """
    Search among classifiers expressed in the log one that is good for the process model extraction

    Parameters
    -----------
    log
        Trace log
    force_activity_transition_insertion
        Optionally force the activitiy+transition classifier insertion

    Returns
    -----------
    log
        Trace log (plus eventually one additional event attribute as the classifier)
    """
    classifier = None
    if log.classifiers and "Activity classifier" in log.classifiers and log.classifiers["Activity classifier"]:
        classifier = "Activity classifier"
    elif log.classifiers and "MXML Legacy Classifier" in log.classifiers and log.classifiers["MXML Legacy Classifier"]:
        classifier = "MXML Legacy Classifier"
    return insert_activity_classifier_attribute(log, classifier,
                                                force_activity_transition_insertion=force_activity_transition_insertion)


def insert_activity_classifier_attribute(log, classifier, force_activity_transition_insertion=False):
    """
    Insert the specified classifier as additional event attribute in the log

    Parameters
    -----------
    log
        Trace log
    classifier
        Event classifier
    force_activity_transition_insertion
        Optionally force the activitiy+transition classifier insertion

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
    elif force_activity_transition_insertion:
        if len(log) > 0 and len(log[0]) > 0 and "concept:name" in log[0][0] and "lifecycle:transition" in log[0][0]:
            classifier_attr_key = "@@classifier"
            for trace in log:
                for event in trace:
                    classifier_value = event["concept:name"] + "+" + event["lifecycle:transition"]
                    event[classifier_attr_key] = classifier_value
    return log, classifier_attr_key


def insert_trace_classifier_attribute(log, classifier):
    """
    Insert the specified classifier as additional trace attribute in the log

    Parameter
    -----------
    log
        Trace log
    classifier
        Event classifier

    Returns
    -----------
    log
        Trace log (plus eventually one additional event attribute as the classifier)
    classifier_attr_key
        Attribute name of the attribute that contains the classifier value
    """
    classifier_attr_key = None
    if classifier is not None:
        classifier_attr_key = "@@traceClassifier"
        for trace in log:
            classifier_value = "+".join([trace.attributes[x] for x in log.classifiers[classifier]])
            trace.attributes[classifier_attr_key] = classifier_value
    return log, classifier_attr_key
