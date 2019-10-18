from pm4py.statistics.traces.log import case_arrival
from pm4py.objects.stochastic_petri import map as mapping
from pm4py.objects.petri.semantics import enabled_transitions, weak_execute
from threading import Thread, Semaphore
from intervaltree import IntervalTree, Interval
from statistics import median
import random
from pm4py.objects.log.log import EventLog, Trace, Event
import datetime


class SimulationThread(Thread):
    def __init__(self, id, net, im, fm, map, start_time, places_interval_trees, transitions_interval_trees,
                 cases_ex_time, list_cases):
        """
        Instantiates the object of the simulation

        Parameters
        -------------
        id
            Identifier
        net
            Petri net
        im
            Initial marking
        fm
            Final marking
        start_time
            Start time
        end_time
            End time
        places_interval_trees
            Dictionary of the interval trees related to the places
        transitions_interval_trees
            Dictionary of the interval trees related to the transitions
        cases_ex_time
            Cases execution time
        list_cases
            Dictionary of cases for each thread
        """
        self.id = id
        self.net = net
        self.im = im
        self.fm = fm
        self.map = map
        self.start_time = start_time
        self.source = list(im)[0]
        self.sink = list(fm)[0]
        self.places_interval_trees = places_interval_trees
        self.transitions_interval_trees = transitions_interval_trees
        self.cases_ex_time = cases_ex_time
        self.list_cases = list_cases
        Thread.__init__(self)

    def run(self):
        """
        Runs the thread
        """
        net, im, fm, map, source, sink, start_time = self.net, self.im, self.fm, self.map, self.source, self.sink, self.start_time
        places_interval_trees = self.places_interval_trees
        transitions_interval_trees = self.transitions_interval_trees
        cases_ex_time = self.cases_ex_time

        current_time = start_time

        source.semaphore.acquire()
        source.assigned_time = max(source.assigned_time, current_time)

        current_marking = im
        et = enabled_transitions(net, current_marking)

        first_event = None
        while not fm <= current_marking or len(et) == 0:
            et = enabled_transitions(net, current_marking)
            ct = random.choice(list(et))

            added_value = -1
            while added_value < 0:
                added_value = map[ct].get_value() if ct in map else 0.0
            ex_time = current_time + added_value
            min_ex_time = ex_time

            for arc in ct.out_arcs:
                place = arc.target
                ex_time = max(place.assigned_time, ex_time)
                place.semaphore.acquire()

            current_time = ex_time

            for arc in ct.out_arcs:
                place = arc.target
                place.assigned_time = current_time

            if ex_time - min_ex_time > 0:
                transitions_interval_trees[ct].add(Interval(min_ex_time, ex_time))

            current_marking = weak_execute(ct, current_marking)

            if ct.label is not None:
                eve = Event({"concept:name": ct.label, "time:timestamp": datetime.datetime.fromtimestamp(current_time)})
                last_event = eve
                if first_event is None:
                    first_event = last_event
                self.list_cases[self.id].append(eve)

            for arc in ct.in_arcs:
                place = arc.source
                p_ex_time = place.assigned_time
                if current_time - p_ex_time > 0:
                    places_interval_trees[place].add(Interval(p_ex_time, current_time))
                place.assigned_time = current_time
                place.semaphore.release()
        # sink.semaphore.release()
        cases_ex_time.append(last_event['time:timestamp'].timestamp() - first_event['time:timestamp'].timestamp())

        for place in current_marking:
            place.semaphore.release()


def apply(log, net, im, fm, parameters=None):
    """
    Performs a Monte Carlo simulation of the Petri net

    Parameters
    -------------
    log
        Event log
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    parameters
        Parameters of the algorithm

    Returns
    ------------
    simulated_log
        Simulated event log
    simulation_result
        Result of the simulation
    """
    if parameters is None:
        parameters = {}

    parameters["business_hours"] = True
    no_simulations = parameters["no_simulations"] if "no_simulations" in parameters else 100
    force_distribution = parameters["force_distribution"] if "force_distribution" in parameters else None

    case_arrival_ratio = parameters[
        "case_arrival_ratio"] if "case_arrival_ratio" in parameters else case_arrival.get_case_arrival_avg(log,
                                                                                                           parameters=parameters)

    places_interval_trees = {}
    transitions_interval_trees = {}
    cases_ex_time = []
    list_cases = {}

    for place in net.places:
        place.semaphore = Semaphore(1)
        place.assigned_time = -1
        places_interval_trees[place] = IntervalTree()
    for trans in net.transitions:
        transitions_interval_trees[trans] = IntervalTree()

    if force_distribution is not None:
        map = mapping.get_map_from_log_and_net(log, net, im, fm, force_distribution=force_distribution,
                                               parameters=parameters)
    else:
        map = mapping.get_map_from_log_and_net(log, net, im, fm, parameters=parameters)

    start_time = 1000000
    threads = []
    for i in range(no_simulations):
        list_cases[i] = Trace()
        t = SimulationThread(i, net, im, fm, map, start_time, places_interval_trees, transitions_interval_trees,
                             cases_ex_time, list_cases)
        t.start()
        threads.append(t)
        start_time = start_time + case_arrival_ratio

    for t in threads:
        t.join()

    log = EventLog(list(list_cases.values()))
    min_timestamp = log[0][0]['time:timestamp'].timestamp()
    max_timestamp = max(y['time:timestamp'].timestamp() for x in log for y in x)

    transitions_interval_trees = {t.name: y for t, y in transitions_interval_trees.items()}

    return log, {"places_interval_trees": places_interval_trees,
                 "transitions_interval_trees": transitions_interval_trees, "cases_ex_time": cases_ex_time,
                 "median_cases_ex_time": median(cases_ex_time), "input_case_arrival_ratio": case_arrival_ratio,
                 "total_time": max_timestamp-min_timestamp}
