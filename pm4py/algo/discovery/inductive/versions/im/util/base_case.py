import logging

def empty_log(log):
    '''Returns bool if log is empty'''
    if len(log) == 0:
        logging.debug("empty_log")
        return True
    else:
        return False


def single_activity(log, activity_key):
    '''Returns bool if log consists of single activity only'''
    if log:
        if len(log[0]) >= 1:
            first_activity = log[0][0][activity_key]
            for i in range(0, len(log)):
                if len(log[i]) != 1 or log[i][0][activity_key] != first_activity:
                    return False                # if there is a trace that has a length not equal to 1, we return false

            # check if all traces consist of the same activity, therefore create dfg from log and get activities of that dfg
            logging_output = "single_activity: " + str(first_activity)
            logging.debug(logging_output)
            return True
        else:
            return False
    else:
        return False
