from typing import Set
from pm4py.objects.dcr.obj import Marking


rels = ['conditionsFor', 'responseTo', 'includesTo', 'excludesTo', 'milestonesFor']

"""
We will implement the semantics according to the papers given in:
DCR 2011, and
Efficient optimal alignment between dynamic condition response graphs and traces
Following the schematic as the pm4py, by using definition function and no class function for this
"""


class DCRSemantics(object):
    """
        the semantics functions implemented is based on the paper by:

        Author: Thomas T. Hildebrandt and Raghava Rao Mukkamala,
        Title: Declarative Event-BasedWorkflow as Distributed Dynamic Condition Response Graphs
        publisher: Electronic Proceedings in Theoretical Computer Science. EPTCS, Open Publishing Association, 2010, pp. 59–73. doi: 10.4204/EPTCS.69.5.
        """
    @classmethod
    def is_enabled(cls, event, graph) -> bool:
        """
        Verify that the given event is enabled for execution in the DCR graph

        Parameters
        ----------
        :param event: the instance of event being check for if enabled
        :param G: DCR graph that it check for being enabled

        Returns
        -------
        :return: true if enabled, false otherwise
        """
        # check if event is enabled, calls function that returns a graph, of enabled events
        return event in cls.enabled(graph)

    @classmethod
    def enabled(cls, graph) -> Set[str]:
        """
        Creates a list of enabled events, based on included events and conditions constraints met

        Parameters
        ----------
        :param graph: takes the current state of the DCR

        Returns
        -------
        :param res: set of enabled activities
        """
        #can be extended to check for milestones
        res = set(graph.marking.included)
        for e in set(graph.conditionsFor.keys()).intersection(res):
            if len(graph.conditionsFor[e].intersection(graph.marking.included.difference(
                    graph.marking.executed))) > 0:
                res.discard(e)
        return res

    @classmethod
    def execute(cls, graph, event):
        """
        Function based on semantics of execution a DCR graph
        will update the graph according to relations of the executed activity

        can extend to allow of execution of milestone activity

        Parameters
        ----------
        :param graph: DCR graph
        :param event: the event being executed

        Returns
        ---------
        :return: DCR graph with updated marking
        """
        #each event is called for execution is called
        if event in graph.marking.pending:
            graph.marking.pending.discard(event)
        graph.marking.executed.add(event)

        #the following if statements are used to provide to update DCR graph
        # depeding on prime event structure within conditions relations
        if event in graph.excludesTo:
            for e_prime in graph.excludesTo[event]:
                graph.marking.included.discard(e_prime)

        if event in graph.includesTo:
            for e_prime in graph.includesTo[event]:
                graph.marking.included.add(e_prime)

        if event in graph.responseTo:
            for e_prime in graph.responseTo[event]:
                graph.marking.pending.add(e_prime)

        return graph

    @classmethod
    def is_accepting(cls, graph) -> bool:
        """
        Checks if the graph is accepting, no included events are pending

        Parameters
        ----------
        :param graph: DCR Graph

        Returns
        ---------
        :return: True if graph is accepting, false otherwise
        """
        res = graph.marking.pending.intersection(graph.marking.included)
        if len(res) > 0:
            return False
        else:
            return True

    @classmethod
    def is_execution_equivalent(cls, marking1: Marking, marking2: Marking) -> bool:
        """
        Verifies if the initial and updated marking is equivalent:
        M'(G) == M''(G)

        Parameters
        ----------
        :param marking1: inital marking
        :param marking2: updated marking
        Returns
        -------
        :return: return true if equivalent, false otherwise
        """
        return (
                marking1.executed == marking2.executed and
                marking1.included == marking2.included and
                marking1.pending == marking2.pending
        )