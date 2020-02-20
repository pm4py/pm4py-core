from pm4py.statistics.traces.log import case_arrival
from pm4py.algo.simulation.montecarlo.utils import replay
from pm4py.objects.petri.semantics import enabled_transitions, weak_execute
from threading import Thread, Semaphore
from intervaltree import IntervalTree, Interval
from statistics import median
import random
from pm4py.objects.log.log import EventLog, Trace, Event
from pm4py.util import constants, xes_constants
import datetime
from time import sleep, time
import logging

PARAM_NUM_SIMULATIONS = "num_simulations"
PARAM_FORCE_DISTRIBUTION = "force_distribution"
PARAM_ENABLE_DIAGNOSTICS = "enable_diagnostics"
PARAM_DIAGN_INTERVAL = "diagn_interval"
PARAM_CASE_ARRIVAL_RATIO = "case_arrival_ratio"
DEFAULT_NUM_SIMULATIONS = 100
DEFAULT_FORCE_DISTRIBUTION = None
DEFAULT_ENABLE_DIAGNOSTICS = True
DEFAULT_DIAGN_INTERVAL = 1.0
DEFAULT_CASE_ARRIVAL_RATIO = None


class SimulationDiagnostics(Thread):
    def __init__(self, sim_thread):
        """
        Initializes the diagnostics thread (for logging purposes)

        Parameters
        -------------
        sim_thread
            Simulation thread
        """
        self.sim_thread = sim_thread
        self.diagn_open = True
        Thread.__init__(self)

    def run(self):
        """
        Runs the diagnostics up to the point in which diagn_open becomes False
        """
        sleep(self.sim_thread.diagn_interval)
        logging.basicConfig()
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        while self.diagn_open:
            pd = {}
            for place in self.sim_thread.net.places:
                if place.semaphore._value == 0:
                    pd[place] = place.semaphore._value
            if pd:
                logger.debug(str(time()) + " diagnostics for thread " + str(
                    self.sim_thread.id) + ": blocked places by semaphore: " + str(pd))
            sleep(self.sim_thread.diagn_interval)


class SimulationThread(Thread):
    def __init__(self, id, net, im, fm, map, start_time, places_interval_trees, transitions_interval_trees,
                 cases_ex_time, list_cases, enable_diagnostics, diagn_interval):
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
        enable_diagnostics
            Enable the logging of diagnostics about the current execution
        diagn_interval
            Interval in which the diagnostics are printed
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
        self.enable_diagnostics = enable_diagnostics
        self.diagn_interval = diagn_interval
        Thread.__init__(self)

    def run(self):
        """
        Runs the thread
        """
        if self.enable_diagnostics:
            diagnostics = SimulationDiagnostics(self)
            diagnostics.start()
        net, im, fm, map, source, sink, start_time = self.net, self.im, self.fm, self.map, self.source, self.sink, self.start_time
        places_interval_trees = self.places_interval_trees
        transitions_interval_trees = self.transitions_interval_trees
        cases_ex_time = self.cases_ex_time

        current_time = start_time

        source.semaphore.acquire()
        source.assigned_time.append(current_time)

        current_marking = im
        et = enabled_transitions(net, current_marking)

        first_event = None
        while not fm <= current_marking or len(et) == 0:
            et = enabled_transitions(net, current_marking)
            ct = random.choice(list(et))

            added_value = -1
            while added_value < 0:
                added_value = map[ct].get_value() if ct in map else 0.0

            current_time0 = current_time

            for arc in ct.out_arcs:
                place = arc.target
                place.semaphore.acquire()
                current_time = max(place.assigned_time.pop(), current_time) if place.assigned_time else current_time

            if current_time - current_time0 > 0:
                transitions_interval_trees[ct].add(Interval(current_time0, current_time))

            current_time = current_time + added_value

            for arc in ct.out_arcs:
                place = arc.target
                place.assigned_time.append(current_time)
                place.assigned_time = sorted(place.assigned_time)

            current_marking = weak_execute(ct, current_marking)

            if ct.label is not None:
                eve = Event({xes_constants.DEFAULT_NAME_KEY: ct.label,
                             xes_constants.DEFAULT_TIMESTAMP_KEY: datetime.datetime.fromtimestamp(current_time)})
                last_event = eve
                if first_event is None:
                    first_event = last_event
                self.list_cases[self.id].append(eve)

            for arc in ct.in_arcs:
                place = arc.source
                p_ex_time = place.assigned_time.pop()
                if current_time - p_ex_time > 0:
                    places_interval_trees[place].add(Interval(p_ex_time, current_time))
                place.assigned_time.append(current_time)
                place.assigned_time = sorted(place.assigned_time)
                place.semaphore.release()
        # sink.semaphore.release()
        cases_ex_time.append(last_event[xes_constants.DEFAULT_TIMESTAMP_KEY].timestamp() - first_event[xes_constants.DEFAULT_TIMESTAMP_KEY].timestamp())

        for place in current_marking:
            place.semaphore.release()

        if self.enable_diagnostics:
            diagnostics.diagn_open = False


def apply(log, net, im, fm, parameters=None):
    """
    Performs a Monte Carlo simulation of a Petri net

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

    timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes_constants.DEFAULT_TIMESTAMP_KEY
    no_simulations = parameters[
        PARAM_NUM_SIMULATIONS] if PARAM_NUM_SIMULATIONS in parameters else DEFAULT_NUM_SIMULATIONS
    force_distribution = parameters[PARAM_FORCE_DISTRIBUTION] if PARAM_FORCE_DISTRIBUTION in parameters else None
    enable_diagnostics = parameters[
        PARAM_ENABLE_DIAGNOSTICS] if PARAM_ENABLE_DIAGNOSTICS in parameters else DEFAULT_ENABLE_DIAGNOSTICS
    diagn_interval = parameters[PARAM_DIAGN_INTERVAL] if PARAM_DIAGN_INTERVAL in parameters else DEFAULT_DIAGN_INTERVAL
    case_arrival_ratio = parameters[
        PARAM_CASE_ARRIVAL_RATIO] if PARAM_CASE_ARRIVAL_RATIO in parameters else DEFAULT_CASE_ARRIVAL_RATIO
    if case_arrival_ratio is None:
        case_arrival_ratio = case_arrival.get_case_arrival_avg(log, parameters=parameters)

    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    places_interval_trees = {}
    transitions_interval_trees = {}
    cases_ex_time = []
    list_cases = {}

    for place in net.places:
        place.semaphore = Semaphore(1)
        place.assigned_time = []
        places_interval_trees[place] = IntervalTree()
    for trans in net.transitions:
        transitions_interval_trees[trans] = IntervalTree()

    if enable_diagnostics:
        logger.info(str(time()) + " started the replay operation.")

    if force_distribution is not None:
        map = replay.get_map_from_log_and_net(log, net, im, fm, force_distribution=force_distribution,
                                              parameters=parameters)
    else:
        map = replay.get_map_from_log_and_net(log, net, im, fm, parameters=parameters)

    if enable_diagnostics:
        logger.info(str(time()) + " ended the replay operation.")

    start_time = 1000000
    threads = []
    for i in range(no_simulations):
        list_cases[i] = Trace()
        t = SimulationThread(i, net, im, fm, map, start_time, places_interval_trees, transitions_interval_trees,
                             cases_ex_time, list_cases, enable_diagnostics, diagn_interval)
        t.start()
        threads.append(t)
        start_time = start_time + case_arrival_ratio

    for t in threads:
        t.join()

    if enable_diagnostics:
        logger.info(str(time()) + " ended the Monte carlo simulation.")

    log = EventLog(list(list_cases.values()))
    min_timestamp = log[0][0][timestamp_key].timestamp()
    max_timestamp = max(y[timestamp_key].timestamp() for x in log for y in x)

    transitions_interval_trees = {t.name: y for t, y in transitions_interval_trees.items()}

    return log, {"places_interval_trees": places_interval_trees,
                 "transitions_interval_trees": transitions_interval_trees, "cases_ex_time": cases_ex_time,
                 "median_cases_ex_time": median(cases_ex_time), "input_case_arrival_ratio": case_arrival_ratio,
                 "total_time": max_timestamp - min_timestamp}
