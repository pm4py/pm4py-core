from pm4py.statistics.traces.log import case_arrival
from pm4py.objects.stochastic_petri import map as mapping
from pm4py.objects.petri.semantics import enabled_transitions, weak_execute
from threading import Thread, Semaphore
from intervaltree import IntervalTree, Interval
from statistics import median
import random


class SimulationThread(Thread):
    def __init__(self, id, net, im, fm, map, start_time, places_interval_trees, transitions_interval_trees,
                 cases_ex_time):
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
        Thread.__init__(self)

    def run(self):
        net, im, fm, map, source, sink, start_time = self.net, self.im, self.fm, self.map, self.source, self.sink, self.start_time
        places_interval_trees = self.places_interval_trees
        transitions_interval_trees = self.transitions_interval_trees
        cases_ex_time = self.cases_ex_time

        current_time = start_time

        source.semaphore.acquire()
        source.assigned_time = max(source.assigned_time, current_time)

        current_marking = im
        et = enabled_transitions(net, current_marking)

        while not fm <= current_marking or len(et) == 0:
            et = enabled_transitions(net, current_marking)
            ct = random.choice(list(et))

            added_value = -1
            while added_value < 0:
                added_value = map[ct].get_value() if ct in map else 0.0
            # if ct in map:
            #    print(map[ct], added_value)
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

            for arc in ct.in_arcs:
                place = arc.source
                p_ex_time = place.assigned_time
                if current_time - p_ex_time > 0:
                    places_interval_trees[place].add(Interval(p_ex_time, current_time))
                place.assigned_time = current_time
                place.semaphore.release()
        # sink.semaphore.release()
        for place in current_marking:
            place.semaphore.release()
        print(self.id, "released")
        cases_ex_time.append(current_time - start_time)


def apply(log, net, im, fm, parameters=None):
    if parameters is None:
        parameters = {}

    parameters["business_hours"] = True
    no_simulations = parameters["no_simulations"] if "no_simulations" in parameters else 10

    case_arrival_ratio = parameters[
        "case_arrival_ratio"] if "case_arrival_ratio" in parameters else case_arrival.get_case_arrival_avg(log,
                                                                  parameters=parameters)

    places_interval_trees = {}
    transitions_interval_trees = {}
    cases_ex_time = []

    for place in net.places:
        place.semaphore = Semaphore(1)
        place.assigned_time = -1
        places_interval_trees[place] = IntervalTree()
    for trans in net.transitions:
        transitions_interval_trees[trans] = IntervalTree()

    map = mapping.get_map_from_log_and_net(log, net, im, fm, parameters=parameters)

    start_time = 0
    threads = []
    for i in range(no_simulations):
        t = SimulationThread(i, net, im, fm, map, start_time, places_interval_trees, transitions_interval_trees,
                             cases_ex_time)
        t.start()
        threads.append(t)
        start_time = start_time + case_arrival_ratio

    for t in threads:
        t.join()

    print(cases_ex_time)
    print(median(cases_ex_time))
