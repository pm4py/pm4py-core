from pm4py.algo.dfg.versions import native as dfg_inst
from pm4py.algo import causal


class ClassicAlphaAbstraction:
    '''
    Class representing the basic abstraction of the alpha miner.
    The class covers start- and end activities, the directly follows relation, the parallel relation and the causal relation.
    '''

    def __init__(self, trace_log, activity_key="concept:name"):
        self.__activity_key = activity_key
        self.__start_activities = self.__derive_start_activities(trace_log)
        self.__end_activities = self.__derive_end_activities(trace_log)
        self.__dfg = {k: v for k, v in dfg_inst.apply(trace_log, activity_key=activity_key).items() if v > 0}
        self.__causal_relations = {k: v for k, v in causal.factory.apply(self.dfg, variant=causal.factory.CAUSAL_ALPHA).items() if v > 0}.keys()
        self.__parallel = {(f, t) for (f, t) in self.dfg if (t, f) in self.dfg}

    def __get_causal_relation(self):
        return self.__causal_relations

    def __get_start_activities(self):
        return self.__start_activities

    def __get_end_activities(self):
        return self.__end_activities

    def __get_directly_follows_graph(self):
        return self.__dfg

    def __get_parallel_relation(self):
        return self.__parallel

    def __get_activity_key(self):
        return self.__activity_key

    def __derive_end_activities(self, trace_log):
        e = set()
        for t in trace_log:
            if len(t) > 0:
                if self.activity_key in t[len(t)-1]:
                    e.add(t[len(t)-1][self.activity_key])
        return e

    def __derive_start_activities(self, trace_log):
        s = set()
        for t in trace_log:
            if len(t) > 0:
                if self.activity_key in t[0]:
                    s.add(t[0][self.activity_key])
        return s

    start_activities = property(__get_start_activities)
    end_activities = property(__get_end_activities)
    dfg = property(__get_directly_follows_graph)
    causal_relation = property(__get_causal_relation)
    parallel_relation = property(__get_parallel_relation)
    activity_key = property(__get_activity_key)
