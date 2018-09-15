from copy import copy
from pm4py.models.petri import semantics
from pm4py.models.petri.petrinet import PetriNet
from statistics import mean, median
from threading import Lock, Thread
from pm4py.visualization.common.utils import *

MAX_NO_THREADS = 1000

class TraceStatistics(Thread):
    def __init__(self, elStatistics, traceIndex, trace, net, initial_marking, activatedTransitions, activity_key, timestamp_key):
        """
        Constructor
        """
        self.elStatistics = elStatistics
        self.traceIndex = traceIndex
        self.trace = trace
        self.net = net
        self.initial_marking = initial_marking
        self.activatedTransitions = activatedTransitions
        self.activity_key = activity_key
        self.timestamp_key = timestamp_key
        Thread.__init__(self)

    def run(self):
        """
        Add statistics on elements based on current trace
        """
        tracePlaceStats = 0
        tracePlaceStats = {}
        if self.timestamp_key in self.trace[0]:
            currentTimestamp = self.trace[0][self.timestamp_key]
        else:
            currentTimestamp = 0
        j = 0
        marking = copy(self.initial_marking)
        for place in marking:
            if not place in self.elStatistics.statistics:
                self.elStatistics.lock.acquire()
                if not place in self.elStatistics.statistics:
                    self.elStatistics.statistics[place] = {"count": 0, "lock":Lock()}
                self.elStatistics.lock.release()
            self.elStatistics.statistics[place]["lock"].acquire()
            self.elStatistics.statistics[place]["count"] = self.elStatistics.statistics[place]["count"] + marking[place]
            self.elStatistics.statistics[place]["lock"].release()
            if not (currentTimestamp == 0):
                tracePlaceStats[place] = [currentTimestamp] * marking[place]
        actTrans = self.activatedTransitions[self.traceIndex]
        z = 0
        while z < len(actTrans):
            trans = actTrans[z]
            if not trans in self.elStatistics.statistics:
                self.elStatistics.lock.acquire()
                if not trans in self.elStatistics.statistics:
                    self.elStatistics.statistics[trans] = {"count": 0, "lock":Lock()}
                self.elStatistics.lock.release()
            self.elStatistics.statistics[trans]["lock"].acquire()
            self.elStatistics.statistics[trans]["count"] = self.elStatistics.statistics[trans]["count"] + 1
            self.elStatistics.statistics[trans]["lock"].release()

            new_marking = semantics.weak_execute(trans, self.net, marking)
            if not new_marking:
                break
            marking_diff = set(new_marking).difference(set(marking))
            for place in marking_diff:
                if not place in self.elStatistics.statistics:
                    self.elStatistics.lock.acquire()
                    if not place in self.elStatistics.statistics:
                        self.elStatistics.statistics[place] = {"count": 0, "lock":Lock()}
                    self.elStatistics.lock.release()
                self.elStatistics.statistics[place]["lock"].acquire()
                self.elStatistics.statistics[place]["count"] = self.elStatistics.statistics[place]["count"] + max(new_marking[place] - marking[place], 1)
                self.elStatistics.statistics[place]["lock"].release()
            marking = new_marking
            if j < len(self.trace):
                if self.timestamp_key in self.trace[j]:
                    currentTimestamp = self.trace[j][self.timestamp_key]
                if trans.label == self.trace[j][self.activity_key]:
                    j = j + 1
            for arc in trans.in_arcs:
                sourcePlace = arc.source
                if not arc in self.elStatistics.statistics:
                    self.elStatistics.lock.acquire()
                    if not arc in self.elStatistics.statistics:
                        self.elStatistics.statistics[arc] = {"performance": [], "count": 0, "lock":Lock()}
                    self.elStatistics.lock.release()
                self.elStatistics.statistics[arc]["lock"].acquire()
                self.elStatistics.statistics[arc]["count"] = self.elStatistics.statistics[arc]["count"] + 1
                self.elStatistics.statistics[arc]["lock"].release()
                if sourcePlace in tracePlaceStats and tracePlaceStats[sourcePlace]:
                    self.elStatistics.statistics[arc]["performance"].append(
                        (currentTimestamp - tracePlaceStats[sourcePlace][0]).total_seconds())
                    del tracePlaceStats[sourcePlace][0]
            for arc in trans.out_arcs:
                targetPlace = arc.target
                if not arc in self.elStatistics.statistics:
                    self.elStatistics.lock.acquire()
                    if not arc in self.elStatistics.statistics:
                        self.elStatistics.statistics[arc] = {"performance": [], "count": 0, "lock":Lock()}
                    self.elStatistics.lock.release()
                self.elStatistics.statistics[arc]["lock"].acquire()
                self.elStatistics.statistics[arc]["count"] = self.elStatistics.statistics[arc]["count"] + 1
                self.elStatistics.statistics[arc]["lock"].release()
                if not currentTimestamp == 0:
                    if not targetPlace in tracePlaceStats:
                        tracePlaceStats[targetPlace] = []
                    tracePlaceStats[targetPlace].append(currentTimestamp)
            z = z + 1

class ElementStatistics(object):
    """
    Collects all element statistics from different threads
    """
    def __init__(self):
        self.lock = Lock()
        self.statistics = {}

def single_element_statistics(log, net, initial_marking, activatedTransitions, activity_key="concept:name", timestamp_key="time:timestamp"):
    """
    Get single Petrinet element statistics

    Parameters
    ------------
    log
        Log
    net
        Petri net
    initial_marking
        Initial marking
    activatedTransitions
        Activated transitions
    activity_key
        Activity key (must be specified if different from concept:name)
    timestamp_key
        Timestamp key (must be specified if different from time:timestamp)

    Returns
    ------------
    statistics
        Petri net element statistics (frequency, unaggregated performance)
    """

    statistics = {}

    elStatistics = ElementStatistics()

    threads = []

    traceIndex = 0
    for trace in log:
        if len(threads) >= MAX_NO_THREADS:
            while len(threads) > 0:
                threads[0].join()
                del threads[0]
        threads.append(TraceStatistics(elStatistics, traceIndex, trace, net, initial_marking, activatedTransitions, activity_key, timestamp_key))
        threads[-1].start()
        traceIndex = traceIndex + 1
    for thread in threads:
        thread.join()

    return elStatistics.statistics

def find_min_max_trans_frequency(statistics):
    """
    Find minimum and maximum transition frequency

    Parameters
    -----------
    statistics
        Element statistics

    Returns
    ----------
    min_frequency
        Minimum transition frequency (in the replay)
    max_frequency
        Maximum transition frequency (in the replay)
    """
    min_frequency = 9999999999
    max_frequency = 0
    for elem in statistics.keys():
        if type(elem) is PetriNet.Transition:
            if statistics[elem]["count"] < min_frequency:
                min_frequency = statistics[elem]["count"]
            if statistics[elem]["count"] > max_frequency:
                max_frequency = statistics[elem]["count"]
    return min_frequency, max_frequency

def find_min_max_arc_frequency(statistics):
    """
    Find minimum and maximum arc frequency

    Parameters
    -----------
    statistics
        Element statistics

    Returns
    -----------
    min_frequency
        Minimum arc frequency
    max_frequency
        Maximum arc frequency
    """
    min_frequency = 9999999999
    max_frequency = 0
    for elem in statistics.keys():
        if type(elem) is PetriNet.Arc:
            if statistics[elem]["count"] < min_frequency:
                min_frequency = statistics[elem]["count"]
            if statistics[elem]["count"] > max_frequency:
                max_frequency = statistics[elem]["count"]
    return min_frequency, max_frequency

def find_min_max_arc_performance(statistics):
    """
    Find minimum and maximum arc performance

    Parameters
    -----------
    statistics
        Element statistics

    Returns
    -----------
    min_performance
        Minimum performance
    max_performance
        Maximum performance
    """
    min_performance = 9999999999
    max_performance = 0
    for elem in statistics.keys():
        if type(elem) is PetriNet.Arc:
            if statistics[elem]["performance"]:
                aggr_stat = mean(statistics[elem]["performance"])
                if aggr_stat < min_performance:
                    min_performance = aggr_stat
                if aggr_stat > max_performance:
                    max_performance = aggr_stat
    return min_performance, max_performance

def aggregate_statistics(statistics, measure="frequency"):
    """
    Gets aggregated statistics

    Parameters
    ----------
    statistics
        Individual element statistics (including unaggregated performances)

    Returns
    ----------
    aggregated_statistics
        Aggregated statistics for arcs, transitions, places
    """
    min_trans_frequency, max_trans_frequency = find_min_max_trans_frequency(statistics)
    min_arc_frequency, max_arc_frequency = find_min_max_arc_frequency(statistics)
    min_arc_performance, max_arc_performance = find_min_max_arc_performance(statistics)
    aggregated_statistics = {}
    for elem in statistics.keys():
        if type(elem) is PetriNet.Arc:
            if measure == "frequency":
                freq = statistics[elem]["count"]
                arc_penwidth = get_arc_penwidth(freq, min_arc_frequency, max_arc_frequency)
                aggregated_statistics[elem] = {"label":str(freq),"penwidth":str(arc_penwidth)}
            elif measure == "performance":
                if statistics[elem]["performance"]:
                    aggr_stat = mean(statistics[elem]["performance"])
                    aggr_stat_hr = human_readable_stat(aggr_stat)
                    arc_penwidth = get_arc_penwidth(aggr_stat, min_arc_performance, max_arc_performance)
                    aggregated_statistics[elem] = {"label":aggr_stat_hr,"penwidth":str(arc_penwidth)}
        elif type(elem) is PetriNet.Transition:
            if measure == "frequency":
                if elem.label is not None:
                    freq = statistics[elem]["count"]
                    color = get_trans_freq_color(freq, min_trans_frequency, max_trans_frequency)
                    aggregated_statistics[elem] = {"label":elem.label+" ("+str(freq)+")", "color": color}
        elif type(elem) is PetriNet.Place:
            pass
    return aggregated_statistics