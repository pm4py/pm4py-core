"""
Shared variables among executions
"""

start = []
end = []
log = None
classifier = "concept:name"
indexed_log = None


def set_log(log_input):
    global log
    log = log_input


def set_start(start_input):
    global start
    start = start_input


def set_end(end_input):
    global end
    end = end_input


def set_classifier(classifier_input):
    global classifier
    classifier = classifier_input


def set_indexed_log(log):
    global indexed_log
    indexed_log = log
