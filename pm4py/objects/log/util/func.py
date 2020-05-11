import warnings

from pm4py.objects.log import log as log_inst


def filter_(func, log):
    '''
    Filters the log according to a given lambda function.

    Parameters
    ----------
    func
    log

    Returns
    -------

    '''
    if isinstance(log, log_inst.EventLog):
        return log_inst.EventLog(list(filter(func, log)), attributes=log.attributes, classifiers=log.classifiers,
                                 omni_present=log.omni_present, extensions=log.extensions)
    elif isinstance(log, log_inst.EventStream):
        return log_inst.EventStream(list(filter(func, log)), attributes=log.attributes, classifiers=log.classifiers,
                                    omni_present=log.omni_present, extensions=log.extensions)
    else:
        warnings.warn('input log object not of appropriate type, filter() not applied')
        return log


def map_(func, log):
    '''
        Maps the log according to a given lambda function.
        domain and target of the function need to be of the same type (either trace or event) otherwise, the map behaves unexpected

        Parameters
        ----------
        func
        log

        Returns
        -------

        '''
    if isinstance(log, log_inst.EventLog):
        return log_inst.EventLog(list(map(func, log)), attributes=log.attributes, classifiers=log.classifiers,
                                 omni_present=log.omni_present, extensions=log.extensions)
    elif isinstance(log, log_inst.EventStream):
        return log_inst.EventStream(list(map(func, log)), attributes=log.attributes, classifiers=log.classifiers,
                                    omni_present=log.omni_present, extensions=log.extensions)
    else:
        warnings.warn('input log object not of appropriate type, map() not applied')
        return log


def sort_(func, log, reverse=False):
    if isinstance(log, log_inst.EventLog):
        return log_inst.EventLog(sorted(log, key=func, reverse=reverse), attributes=log.attributes,
                                 classifiers=log.classifiers, omni_present=log.omni_present, extensions=log.extensions)
    elif isinstance(log, log_inst.EventStream):
        return log_inst.EventStream(sorted(log, key=func, reverse=reverse), attributes=log.attributes,
                                    classifiers=log.classifiers,
                                    omni_present=log.omni_present, extensions=log.extensions)
    else:
        warnings.warn('input log object not of appropriate type, map() not applied')
        return log
