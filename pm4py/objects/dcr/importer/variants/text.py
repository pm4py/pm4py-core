def readGraph(graph, graph_path):
    '''
    timings will be loaded from the ISO 8601 duration format
    :param graph_path:
    :param has_timings:
    :return:
    '''
    with open(graph_path) as f:
        lines = f.readlines()

    timings = {} # timings in ISO 8601 duration format

    for line in lines:
        if line.startswith('EVENT'):
            graph['events'].append(line.split(';',maxsplit=1)[1])
        elif line.startswith('CONDITION'):
            condition = line.split(';')[1:]
            # In the python representations the conditions For are indexed by the end event
            if condition[0] in graph['conditionsFor'].keys():
                graph['conditionsFor'][condition[1]].append(condition[0])
            else:
                graph['conditionsFor'][condition[1]] = [condition[0]]
            if len(condition)>2:
                timings[('CONDITION',condition[0],condition[1])] = condition[3]

        elif line.startswith('RESPONSE'):
            response = line.split(';')[1:]
            if response[0] in graph['responseTo'].keys():
                graph['responseTo'][response[0]].append(response[1])
            else:
                graph['responseTo'][response[0]] = [response[1]]
            if len(response)>2:
                timings[('RESPONSE',response[0],response[1])] = response[3]
        elif line.startswith('EXCLUDE'):
            exclude = line.split(';')[1:]
            if exclude[0] in graph['excludesTo'].keys():
                graph['excludesTo'][exclude[0]].append(exclude[1])
            else:
                graph['excludesTo'][exclude[0]] = [exclude[1]]
        elif line.startswith('INCLUDE'):
            include = line.split(';')[1:]
            if include[0] in graph['includesTo'].keys():
                graph['includesTo'][include[0]].append(include[1])
            else:
                graph['includesTo'][include[0]] = [include[1]]
        else:
            print(f'[x] Unsupported line: {line}')
    return graph, timings