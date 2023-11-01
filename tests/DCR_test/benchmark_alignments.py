import pm4py
import pandas as pd
import matplotlib.pyplot as plt
import time
import logging
import cProfile
from collections import Counter

from pm4py.algo.discovery.dcr_discover.algorithm import apply
from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
from pm4py.algo.conformance.alignments.dcr.variants import optimal
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.conformance.alignments.dfg.variants import classic
from pm4py.algo.discovery.dfg.variants import performance


def apply_trace_to_log(training_log, G):
    print("Inside apply_trace_to_log function.")
    graph_handler = optimal.DCRGraphHandler(G)
    trace_handler = optimal.TraceHandler(training_log, 'concept:name')
    print("About to create Alignment object.")
    alignment_obj = optimal.Alignment(graph_handler, trace_handler)
    print("About to call apply_trace on Alignment object.")
    return alignment_obj.apply_trace()


def benchmark_optimal():
    repeat = 10
    times = []
    no_event = []
    no_of_act = []

    for i in range(1, 11):
        print(f"Starting iteration {i}")
        result = []
        print("Reading and converting log...")
        training_log = pm4py.read_xes('../input_data/pdc/pdc_2019/Training Logs/pdc_2019_' + str(i) + '.xes')
        add = pd.date_range('2018-04-09', periods=len(training_log), freq='20min')
        training_log['time:timestamp'] = add

        # Convert DataFrame to EventLog
        if isinstance(training_log, pd.DataFrame):
            training_log = log_converter.apply(training_log)
        print("Generating DCR graph...")
        # Generate DCR graph
        dcr_result = apply(training_log, dcr_discover)
        G = dcr_result[0]

        # Benchmarking
        warm_up_runs = 1
        print("Starting warm-up runs...")
        for idx in range(warm_up_runs):
            print(f"Warm-up run {idx + 1}")
            apply_trace_to_log(training_log, G)
        print("Completed warm-up runs.")

        for _ in range(repeat):
            starttime = time.perf_counter()
            apply_trace_to_log(training_log, G)
            endtime = time.perf_counter() - starttime
            result.append(endtime)
            print(f"Completed benchmarking for iteration {i}.")

        avg_time = (sum(result) / repeat) * 1000
        print(f"Result from test {i}: {avg_time} ms")

        # Counting number of events and activities
        num_events = sum(len(trace) for trace in training_log)
        activities = set(event['concept:name'] for trace in training_log for event in trace)

        print(f"Length of event log: {num_events}")
        print(f"Number of activities: {len(activities)}")

        times.append(avg_time)
        no_event.append(num_events)
        no_of_act.append(len(activities))

    # Plotting
    x = [i for i in range(1, 11)]
    y = times
    plt.plot(x, times, label='Optimal')
    plt.ylabel('Run time in ms')
    plt.xlabel('PDC logs 1 to 10')
    plt.grid(axis='x')
    plt.grid(axis='y')
    plt.show()


def benchmark_dfg_alignment():
    repeat = 10

    times = []

    for i in range(1, 11):
        result = []

        training_log = pm4py.read_xes('../input_data/pdc/pdc_2019/Training Logs/pdc_2019_' + str(i) + '.xes')
        add = pd.date_range('2018-04-09', periods=len(training_log), freq='20min')
        training_log['time:timestamp'] = add

        # Convert DataFrame to EventLog
        if isinstance(training_log, pd.DataFrame):
            training_log = log_converter.apply(training_log)
        print("Generating DFG...")
        # Generate DFG
        params = {}
        dfg_result = performance.apply(training_log, params)

        G = dfg_result
        # print(f"type of dfg: {type(G)}, contents of dfg: {G}")

        start_activities = [trace[0]['concept:name'] for trace in training_log]
        sa = Counter(start_activities)
        end_activities = [trace[-1]['concept:name'] for trace in training_log]
        ea = Counter(end_activities)
        sa = dict(sa)
        ea = dict(ea)

        # Warm up
        for _ in range(1):
            classic.apply(training_log, G, sa, ea)

        # Benchmark classic
        for _ in range(repeat):
            starttime = time.perf_counter()
            classic.apply(training_log, G, sa, ea)
            endtime = time.perf_counter() - starttime
            result.append(endtime)

        avg_time_classic = (sum(result) / repeat) * 1000

        print(f"Result from test {i}: Classic {avg_time_classic} ms")

        times.append(avg_time_classic)

    # Plotting
    x = [i for i in range(1, 11)]
    plt.plot(x, times, label='Classic')
    plt.ylabel('Run time in ms')
    plt.xlabel('PDC logs 1 to 10')
    plt.legend()
    plt.grid(axis='x')
    plt.grid(axis='y')
    plt.show()


def benchmark_optimal2():
    repeat = 10
    times = []
    no_event = []
    no_of_act = []

    for i in range(1, 11):
        logging.info(f"Starting iteration {i}")
        result = []
        logging.info("Reading and converting log...")

        training_log = pm4py.read_xes('../input_data/pdc/pdc_2019/Training Logs/pdc_2019_' + str(i) + '.xes')
        add = pd.date_range('2018-04-09', periods=len(training_log), freq='20min')
        training_log['time:timestamp'] = add

        # Convert DataFrame to EventLog
        if isinstance(training_log, pd.DataFrame):
            training_log = log_converter.apply(training_log)

        logging.info("Generating DCR graph...")

        dcr_result = apply(training_log, dcr_discover)
        G = dcr_result[0]

        # Benchmarking
        warm_up_runs = 1
        logging.info("Starting warm-up runs...")
        for idx in range(warm_up_runs):
            logging.info(f"Warm-up run {idx + 1}")
            apply_trace_to_log(training_log, G)
        logging.info("Completed warm-up runs.")

        for _ in range(repeat):
            pr = cProfile.Profile()
            pr.enable()

            start_time = time.perf_counter()
            apply_trace_to_log(training_log, G)
            end_time = time.perf_counter() - start_time

            pr.disable()
            pr.print_stats(sort='cumulative')

            result.append(end_time)
            logging.info(f"Completed benchmarking for iteration {i}.")

        avg_time = (sum(result) / repeat) * 1000
        logging.info(f"Result from test {i}: {avg_time} ms")

        num_events = sum(len(trace) for trace in training_log)
        activities = set(event['concept:name'] for trace in training_log for event in trace)

        times.append(avg_time)
        no_event.append(num_events)
        no_of_act.append(len(activities))

    # Plotting
    x = [i for i in range(1, 11)]
    y = times
    plt.plot(x, times, label='Optimal')
    plt.ylabel('Run time in ms')
    plt.xlabel('PDC logs 1 to 10')
    plt.grid(axis='x')
    plt.grid(axis='y')
    plt.show()



if __name__ == "__main__":
    print("Running benchmark for optimal...")
    # benchmark_optimal()
    benchmark_optimal2()
    # print("Running benchmark for classc")
    # benchmark_dfg_alignment()


