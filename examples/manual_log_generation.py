from copy import deepcopy

from pm4py.objects.log.obj import EventLog, Trace, Event


def execute_script():
    L = EventLog()
    e1 = Event()
    e1["concept:name"] = "A"
    e2 = Event()
    e2["concept:name"] = "B"
    e3 = Event()
    e3["concept:name"] = "C"
    e4 = Event()
    e4["concept:name"] = "D"
    t = Trace()
    t.append(e1)
    t.append(e2)
    t.append(e3)
    t.append(e4)
    for i in range(10000):
        L.append(deepcopy(t))
    print(len(L))


if __name__ == "__main__":
    execute_script()
