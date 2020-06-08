def apply(file_path, parameters=None):
    """
    Import a DFG (along with the start and end activities) from a .dfg file

    Parameters
    --------------
    file_path
        Path of the DFG file
    parameters
        Possible parameters of the algorithm

    Returns
    --------------
    dfg
        DFG
    start_activities
        Start activities
    end_activities
        End activities
    """
    if parameters is None:
        parameters = {}

    F = open(file_path, "r")
    content = F.readlines()
    F.close()

    activities = []
    start_activities = {}
    end_activities = {}
    dfg = {}

    num_activities = int(content[0])
    i = 1
    while i <= num_activities:
        activities.append(content[i].strip())
        i = i + 1

    num_sa = int(content[i])

    target = i + num_sa
    i = i + 1

    while i <= target:
        act, count = content[i].strip().split("x")
        act = activities[int(act)]
        count = int(count)
        start_activities[act] = count
        i = i + 1

    num_ea = int(content[i])

    target = i + num_ea
    i = i + 1

    while i <= target:
        act, count = content[i].strip().split("x")
        act = activities[int(act)]
        count = int(count)
        end_activities[act] = count
        i = i + 1

    while i < len(content):
        acts, count = content[i].strip().split("x")
        count = int(count)
        a1, a2 = acts.split(">")
        a1 = activities[int(a1)]
        a2 = activities[int(a2)]
        dfg[(a1, a2)] = count
        i = i + 1

    return dfg, start_activities, end_activities

