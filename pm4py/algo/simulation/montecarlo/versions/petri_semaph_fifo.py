from pm4py.statistics.traces.log import case_arrival
from pm4py.algo.simulation.montecarlo.utils import replay
from pm4py.objects.petri.semantics import enabled_transitions, weak_execute
from threading import Thread, Semaphore
from intervaltree import IntervalTree, Interval
from statistics import median
from pm4py.objects.log.log import EventLog, Trace, Event
from pm4py.util import constants, xes_constants
from pm4py.objects.stochastic_petri import utils as stochastic_utils
import datetime
from time import sleep, time
import logging

PARAM_NUM_SIMULATIONS = "num_simulations"
PARAM_FORCE_DISTRIBUTION = "force_distribution"
PARAM_ENABLE_DIAGNOSTICS = "enable_diagnostics"
PARAM_DIAGN_INTERVAL = "diagn_interval"
PARAM_CASE_ARRIVAL_RATIO = "case_arrival_ratio"
PARAM_PROVIDED_SMAP = "provided_stochastic_map"
PARAM_MAP_RESOURCES_PER_PLACE = "map_resources_per_place"
PARAM_DEFAULT_NUM_RESOURCES_PER_PLACE = "default_num_resources_per_place"
PARAM_SMALL_SCALE_FACTOR = "small_scale_factor"
PARAM_MAX_THREAD_EXECUTION_TIME = "max_thread_exec_time"
DEFAULT_NUM_SIMULATIONS = 100
DEFAULT_FORCE_DISTRIBUTION = None
DEFAULT_ENABLE_DIAGNOSTICS = True
# 32 seconds between diagnostics prints
DEFAULT_DIAGN_INTERVAL = 32.0
DEFAULT_CASE_ARRIVAL_RATIO = None
DEFAULT_PROVIDED_SMAP = None
DEFAULT_MAP_RESOURCES_PER_PLACE = None
DEFAULT_DEFAULT_NUM_RESOURCES_PER_PLACES = 1
# 1 second in the simulation corresponds to 10gg
DEFAULT_SMALL_SCALE_FACTOR = 864000.0
# 1 min to finish a thread
DEFAULT_MAX_THREAD_EXECUTION_TIME = 60.0

OUTPUT_PLACES_INTERVAL_TREES = "places_interval_trees"
OUTPUT_TRANSITIONS_INTERVAL_TREES = "transitions_interval_trees"
OUTPUT_CASES_EX_TIME = "cases_ex_time"
OUTPUT_MEDIAN_CASES_EX_TIME = "median_cases_ex_time"
OUTPUT_CASE_ARRIVAL_RATIO = "input_case_arrival_ratio"
OUTPUT_TOTAL_CASES_TIME = "total_cases_time"

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
                logger.info(str(time()) + " diagnostics for thread " + str(
                    self.sim_thread.id) + ": blocked places by semaphore: " + str(pd))
            sleep(self.sim_thread.diagn_interval)


class SimulationThread(Thread):
    def __init__(self, id, net, im, fm, map, start_time, places_interval_trees, transitions_interval_trees,
                 cases_ex_time, list_cases, enable_diagnostics, diagn_interval, small_scale_factor, max_thread_exec_time):
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
        self.small_scale_factor = small_scale_factor
        self.max_thread_exec_time = max_thread_exec_time
        self.internal_thread_start_time = 0
        self.terminated_correctly = False
        Thread.__init__(self)

    def get_rem_time(self):
        return max(0, self.max_thread_exec_time - (time() - self.internal_thread_start_time))

    def run(self):
        """
        Runs the thread
        """
        if self.enable_diagnostics:
            diagnostics = SimulationDiagnostics(self)
            diagnostics.start()

        logging.basicConfig()
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        net, im, fm, smap, source, sink, start_time = self.net, self.im, self.fm, self.map, self.source, self.sink, self.start_time
        places_interval_trees = self.places_interval_trees
        transitions_interval_trees = self.transitions_interval_trees
        cases_ex_time = self.cases_ex_time

        current_time = start_time

        self.internal_thread_start_time = time()
        rem_time = self.get_rem_time()

        acquired_places = set()
        acquired = source.semaphore.acquire(timeout=rem_time)
        if acquired:
            acquired_places.add(source)
        source.assigned_time.append(current_time)

        current_marking = im
        et = enabled_transitions(net, current_marking)

        first_event = None
        last_event = None

        while not fm <= current_marking or len(et) == 0:
            et = list(enabled_transitions(net, current_marking))
            ct = stochastic_utils.pick_transition(et, smap)

            simulated_execution_plus_waiting_time = -1
            while simulated_execution_plus_waiting_time < 0:
                simulated_execution_plus_waiting_time = smap[ct].get_value() if ct in smap else 0.0

            # establish how much time we need to wait before firing the transition
            # (it depends on the input places tokens)
            waiting_time = 0
            for arc in ct.out_arcs:
                place = arc.target
                sem_value = int(place.semaphore._value)
                rem_time = self.get_rem_time()
                acquired = place.semaphore.acquire(timeout=rem_time)
                if acquired:
                    acquired_places.add(place)
                rem_time = self.get_rem_time()
                if rem_time == 0:
                    break
                if sem_value == 0:
                    waiting_time = max(waiting_time,
                                       place.assigned_time.pop(
                                           0) - current_time) if place.assigned_time else waiting_time

            if rem_time == 0:
                for place in acquired_places:
                    place.semaphore.release()
                break

            # if the waiting time is greater than 0, add an interval to the interval tree denoting
            # the waiting times for the given transition
            if waiting_time > 0:
                transitions_interval_trees[ct].add(Interval(current_time, current_time + waiting_time))

            # get the actual execution time of the transition as a difference between simulated_execution_plus_waiting_time
            # and the waiting time
            execution_time = max(simulated_execution_plus_waiting_time - waiting_time, 0)

            # increase the timing based on the waiting time and the execution time of the transition
            current_time = current_time + waiting_time + execution_time

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
                p_ex_time = place.assigned_time.pop(0)
                if current_time - p_ex_time > 0:
                    places_interval_trees[place].add(Interval(p_ex_time, current_time))
                place.assigned_time.append(current_time)
                place.assigned_time = sorted(place.assigned_time)
                place.semaphore.release()

            # sleep before starting next iteration
            sleep((waiting_time + execution_time) / self.small_scale_factor)

        if first_event is not None and last_event is not None:
            cases_ex_time.append(last_event[xes_constants.DEFAULT_TIMESTAMP_KEY].timestamp() - first_event[
                xes_constants.DEFAULT_TIMESTAMP_KEY].timestamp())
        else:
            cases_ex_time.append(0)

        places_to_free = set(current_marking).union(acquired_places)

        for place in places_to_free:
            place.semaphore.release()

        rem_time = self.get_rem_time()
        if rem_time > 0:
            self.terminated_correctly = True
            logger.info(str(time()) + " terminated successfully thread ID " + str(self.id))

        if self.enable_diagnostics:
            if rem_time == 0:
                logger.info(str(time()) + " terminated for timeout thread ID " +str(self.id))

        if self.enable_diagnostics:
            diagnostics.diagn_open = False


def apply(log, net, im, fm, parameters=None):
    """
    Performs a Monte Carlo simulation of an accepting Petri net without duplicate transitions and where the preset is always
    distinct from the postset (FIFO variant; the semaphores pile up if waiting is needed, and the first in is the first to win
    the semaphore)

    Parameters
    -------------
    log
        Event log
    net
        Accepting Petri net without duplicate transitions and where the preset is always distinct from the postset
    im
        Initial marking
    fm
        Final marking
    parameters
        Parameters of the algorithm:
            PARAM_NUM_SIMULATIONS => (default: 100)
            PARAM_FORCE_DISTRIBUTION => Force a particular stochastic distribution (e.g. normal) when the stochastic map
            is discovered from the log (default: None; no distribution is forced)
            PARAM_ENABLE_DIAGNOSTICS => Enable the printing of diagnostics (default: True)
            PARAM_DIAGN_INTERVAL => Interval of time in which diagnostics of the simulation are printed (default: 32)
            PARAM_CASE_ARRIVAL_RATIO => Case arrival of new cases (default: None; inferred from the log)
            PARAM_PROVIDED_SMAP => Stochastic map that is used in the simulation (default: None; inferred from the log)
            PARAM_MAP_RESOURCES_PER_PLACE => Specification of the number of resources available per place
            (default: None; each place gets the default number of resources)
            PARAM_DEFAULT_NUM_RESOURCES_PER_PLACE => Default number of resources per place when not specified
            (default: 1; each place gets 1 resource and has to wait for the resource to finish)
            PARAM_SMALL_SCALE_FACTOR => Scale factor for the sleeping time of the actual simulation
            (default: 864000.0, 10gg)
            PARAM_MAX_THREAD_EXECUTION_TIME => Maximum execution time per thread (default: 60.0, 1 minute)

    Returns
    ------------
    simulated_log
        Simulated event log
    simulation_result
        Result of the simulation:
            OUTPUT_PLACES_INTERVAL_TREES => inteval trees that associate to each place the times in which it was occupied.
            OUTPUT_TRANSITIONS_INTERVAL_TREES => interval trees that associate to each transition the intervals of time
            in which it could not fire because some token was in the output.
            OUTPUT_CASES_EX_TIME => Throughput time of the cases included in the simulated log
            OUTPUT_MEDIAN_CASES_EX_TIME => Median of the throughput times
            OUTPUT_CASE_ARRIVAL_RATIO => Case arrival ratio that was specified in the simulation
            OUTPUT_TOTAL_CASES_TIME => Total time occupied by cases of the simulated log
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
    smap = parameters[PARAM_PROVIDED_SMAP] if PARAM_PROVIDED_SMAP in parameters else DEFAULT_PROVIDED_SMAP
    resources_per_places = parameters[
        PARAM_MAP_RESOURCES_PER_PLACE] if PARAM_MAP_RESOURCES_PER_PLACE in parameters else DEFAULT_MAP_RESOURCES_PER_PLACE
    default_num_resources_per_places = parameters[
        PARAM_DEFAULT_NUM_RESOURCES_PER_PLACE] if PARAM_DEFAULT_NUM_RESOURCES_PER_PLACE in parameters else DEFAULT_DEFAULT_NUM_RESOURCES_PER_PLACES
    small_scale_factor = parameters[
        PARAM_SMALL_SCALE_FACTOR] if PARAM_SMALL_SCALE_FACTOR in parameters else DEFAULT_SMALL_SCALE_FACTOR
    max_thread_exec_time = parameters[
        PARAM_MAX_THREAD_EXECUTION_TIME] if PARAM_MAX_THREAD_EXECUTION_TIME in parameters else DEFAULT_MAX_THREAD_EXECUTION_TIME

    if case_arrival_ratio is None:
        case_arrival_ratio = case_arrival.get_case_arrival_avg(log, parameters=parameters)
    if resources_per_places is None:
        resources_per_places = {}

    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    places_interval_trees = {}
    transitions_interval_trees = {}
    cases_ex_time = []
    list_cases = {}

    for place in net.places:
        # assign a semaphore to each place.
        if place in resources_per_places:
            place.semaphore = Semaphore(resources_per_places[place])
        else:
            # if the user does not specify the number of resources per place,
            # the default number is used
            place.semaphore = Semaphore(default_num_resources_per_places)
        place.assigned_time = []
        places_interval_trees[place] = IntervalTree()
    for trans in net.transitions:
        transitions_interval_trees[trans] = IntervalTree()

    # when the user does not specify any map from transitions to random variables,
    # a replay operation is performed
    if smap is None:
        if enable_diagnostics:
            logger.info(str(time()) + " started the replay operation.")
        if force_distribution is not None:
            smap = replay.get_map_from_log_and_net(log, net, im, fm, force_distribution=force_distribution,
                                                   parameters=parameters)
        else:
            smap = replay.get_map_from_log_and_net(log, net, im, fm, parameters=parameters)
        if enable_diagnostics:
            logger.info(str(time()) + " ended the replay operation.")

    # the start timestamp is set to 1000000 instead of 0 to avoid problems with 32 bit machines
    start_time = 1000000
    threads = []
    for i in range(no_simulations):
        list_cases[i] = Trace()
        t = SimulationThread(i, net, im, fm, smap, start_time, places_interval_trees, transitions_interval_trees,
                             cases_ex_time, list_cases, enable_diagnostics, diagn_interval, small_scale_factor,
                             max_thread_exec_time)
        t.start()
        threads.append(t)
        start_time = start_time + case_arrival_ratio
        # wait a factor before opening a thread and the next one
        sleep(case_arrival_ratio / small_scale_factor)

    for t in threads:
        t.join()

    i = 0
    while i < len(threads):
        if threads[i].terminated_correctly is False:
            del list_cases[threads[i].id]
            del threads[i]
            del cases_ex_time[i]
            continue
        i = i + 1

    if enable_diagnostics:
        logger.info(str(time()) + " ended the Monte carlo simulation.")

    log = EventLog(list(list_cases.values()))
    min_timestamp = log[0][0][timestamp_key].timestamp()
    max_timestamp = max(y[timestamp_key].timestamp() for x in log for y in x)

    transitions_interval_trees = {t.name: y for t, y in transitions_interval_trees.items()}

    return log, {OUTPUT_PLACES_INTERVAL_TREES: places_interval_trees,
                 OUTPUT_TRANSITIONS_INTERVAL_TREES: transitions_interval_trees, OUTPUT_CASES_EX_TIME: cases_ex_time,
                 OUTPUT_MEDIAN_CASES_EX_TIME: median(cases_ex_time), OUTPUT_CASE_ARRIVAL_RATIO: case_arrival_ratio,
                 OUTPUT_TOTAL_CASES_TIME: max_timestamp - min_timestamp}
