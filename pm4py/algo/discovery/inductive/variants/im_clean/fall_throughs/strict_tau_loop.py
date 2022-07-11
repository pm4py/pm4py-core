from typing import Optional

from pm4py.objects.log.obj import EventLog, Trace


def detect(log: EventLog, start_activities, end_activities) -> Optional[EventLog]:
    proj = []
    for t in log:
        x = 0
        for i in range(1, len(t)):
            if t[i] in start_activities and t[i - 1] in end_activities:
                proj.append(t[x:i])
                x = i
        proj.append(t[x:len(t)])
    return proj if len(proj) > len(log) else None
