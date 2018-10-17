from pm4py.algo.discovery.causal import factory as causal_factory
from pm4py.algo.discovery.causal.factory import CAUSAL_ALPHA


class ClassicAlphaAbstraction:
    """
    Class representing the basic abstraction of the alpha miner.
    The class covers start- and end attributes, the directly follows relation, the parallel relation and the causal
    relation.
    """

    def __init__(self, start_activities, end_activities, dfg, activity_key="concept:name"):
        self.__activity_key = activity_key
        self.__start_activities = start_activities
        self.__end_activities = end_activities
        self.__dfg = dfg
        self.__causal_relations = {k: v for k, v in causal_factory.apply(self.dfg, variant=CAUSAL_ALPHA).items() if
                                   v > 0}.keys()
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

    start_activities = property(__get_start_activities)
    end_activities = property(__get_end_activities)
    dfg = property(__get_directly_follows_graph)
    causal_relation = property(__get_causal_relation)
    parallel_relation = property(__get_parallel_relation)
    activity_key = property(__get_activity_key)
