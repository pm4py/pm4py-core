def writeGraph(graph,graph_path,timings=None):
    '''
    timings will be saved into the ISO 8601 duration format
    :param graph_path:
    :param timings:
    :return:
    '''
    data = ''
    withTimings = False
    if timings:
        withTimings = True

    for event in graph['events']:
        data = data + 'EVENT;' + event + '\n'

    for endEvent in graph['conditionsFor']:
        for startEvent in graph['conditionsFor'][endEvent]:
            if withTimings and (('CONDITION',startEvent,endEvent) in timings.keys()):
                data = data + 'CONDITION;' + startEvent + ';' + endEvent + ';' + 'DELAY;P' + str(int(timings[('CONDITION',startEvent,endEvent)])) +'D\n'
            else:
                data = data + 'CONDITION;' + startEvent + ';' + endEvent + '\n'

    for startEvent in graph['responseTo']:
        for endEvent in graph['responseTo'][startEvent]:
            if withTimings and (('RESPONSE',startEvent,endEvent) in timings.keys()):
                data = data + 'RESPONSE;' + startEvent + ';' + endEvent + ';' + 'DEADLINE;P' + str(int(timings[('RESPONSE',startEvent,endEvent)])) +'D\n'
            else:
                data = data + 'RESPONSE;' + startEvent + ';' + endEvent + '\n'

    for startEvent in graph['excludesTo']:
        for endEvent in graph['excludesTo'][startEvent]:
            data = data + 'EXCLUDE;'+ startEvent + ';' + endEvent + '\n'

    for startEvent in graph['includesTo']:
        for endEvent in graph['includesTo'][startEvent]:
            data = data + 'INCLUDE;'+ startEvent + ';' + endEvent + '\n'

    with open(graph_path,'w+') as f:
        f.write(data)


def write_with_lifecycle_subprocesses(graph, graph_path, timings):
    data = ''
    withTimings = False
    if timings:
        withTimings = True

    complete_notation = ':Complete'
    subprocesses = {}
    for startEvent in graph['excludesTo']:
        for endEvent in graph['excludesTo'][startEvent]:
            if startEvent == endEvent:
                if startEvent not in subprocesses.keys():
                    subprocesses[startEvent] = set()
                subprocesses[startEvent].add(f'{startEvent}{complete_notation}')

    for event in graph['events']:
        data = data + 'EVENT;' + event + '\n'

    for subprocess_name, subprocess_events in subprocesses.items():
        sub_events = '['
        for event in subprocess_events:
            sub_events = sub_events + event + ';'
        sub_events = sub_events[:-1] + ']'
        data = data + 'SUBPROCESS;' + subprocess_name + sub_events + '\n'

    for endEvent in graph['conditionsFor']:
        for startEvent in graph['conditionsFor'][endEvent]:
            if withTimings and (('CONDITION', startEvent, endEvent) in timings.keys()):
                data = data + 'CONDITION;' + startEvent + ';' + endEvent + ';' + 'DELAY;P' + str(
                    int(timings[('CONDITION', startEvent, endEvent)])) + 'D\n'
            else:
                data = data + 'CONDITION;' + startEvent + ';' + endEvent + '\n'

    for startEvent in graph['responseTo']:
        for endEvent in graph['responseTo'][startEvent]:
            if withTimings and (('RESPONSE', startEvent, endEvent) in timings.keys()):
                data = data + 'RESPONSE;' + startEvent + ';' + endEvent + ';' + 'DEADLINE;P' + str(
                    int(timings[('RESPONSE', startEvent, endEvent)])) + 'D\n'
            else:
                data = data + 'RESPONSE;' + startEvent + ';' + endEvent + '\n'

    for startEvent in graph['excludesTo']:
        for endEvent in graph['excludesTo'][startEvent]:
            if startEvent == endEvent:
                data = data + f'EXCLUDE;{startEvent}{complete_notation};{endEvent}{complete_notation}\n'
            else:
                data = data + 'EXCLUDE;' + startEvent + ';' + endEvent + '\n'

    for startEvent in graph['includesTo']:
        for endEvent in graph['includesTo'][startEvent]:
            data = data + 'INCLUDE;' + startEvent + ';' + endEvent + '\n'

    with open(graph_path, 'w+') as f:
        f.write(data)