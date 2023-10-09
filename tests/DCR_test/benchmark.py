import pm4py
import pandas as pd
import matplotlib.pyplot as plt
import time

def benchmark_discover():
    from pm4py.discovery import discover_dcr
    repeat = 10
    times = []
    no_event = []
    no_of_act = []
    for i in range(1, 11):
        result = []
        training_log = pm4py.read_xes('../input_data/pdc/pdc_2019/Training Logs/pdc_2019_' + str(i) + '.xes')
        add = pd.date_range('2018-04-09', periods=len(training_log), freq='20min')
        training_log['time:timestamp'] = add
        discover_dcr(training_log)
        for i in range(repeat):
            starttime = time.perf_counter()
            discover_dcr(training_log)
            endtime = time.perf_counter() - starttime
            result.append(endtime)

        print("result from test: " + str(i) + ": " + str((sum(result) / repeat) * 1000) + " ms")
        print("length of event log: " + str(len(training_log)))
        print("number of actitivies: " + str(len(set(training_log['concept:name']))))
        times.append((sum(result)/repeat) * 1000)
        no_event.append(len(training_log))
        no_of_act.append(len(set(training_log['concept:name'])))

    x = [i for i in range(1, 11)]
    y = times
    plt.plot(x, y)
    plt.ylabel('run time in ms')
    plt.xlabel('pdc logs 1 to 10')
    plt.grid(axis='x')
    plt.grid(axis='y')
    plt.show()

if __name__ == "__main__":
    benchmark_discover()





