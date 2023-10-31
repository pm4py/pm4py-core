from copy import deepcopy
#from datetime import timedelta
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
    def is_enabled(cls, event, dcr) -> bool:
        """
        Function for semantic for checking if event is enabled

        Parameters
        ----------
        :param event: the instance of event being check for if enabled
        :param dcr: DCR graph that it check for being enabled

        Returns
        -------
        :return: true if enabled, false otherwise
        """
        # check if event is enabled, calls function that returns a graph, of enabled events
        return event in cls.enabled(dcr)

    @classmethod
    def enabled(cls, dcr) -> Set[str]:
        """
        Function to that based on sematics for enabled behavior returns a set of allowed activities to execute
        can be extended to check milestone
        Parameters
        ----------
        :param dcr: takes the current state of the DCR

        Returns
        -------
        :param res: set of enabled activities
        """
        res = deepcopy(dcr.marking.included)
        for e in set(dcr.conditionsFor.keys()).intersection(res):
            if len(dcr.conditionsFor[e].intersection(dcr.marking.included.difference(
                    dcr.marking.executed))) > 0:
                res.discard(e)
        return res

    @classmethod
    def execute(cls, dcr, event):
        """
        Function based on semantics of execution a DCR graph
        will update the graph according to relations of the executed activity

        can extend to allow of execution of milestone activity

        Parameters
        ----------
        :param dcr: The current state of DCR graph, with activities and their relatiosn
        :param e: the event being executed the type activity being executed

        Returns
        -------
        :return dcr: return the updated state of DCR graph

        """
        #each event is called for execution is called
        if event in dcr.marking.pending:
            dcr.marking.pending.discard(event)
        dcr.marking.executed.add(event)

        #the following if statements are used to provide to update DCR graph
        # depeding on prime event structure within conditions relations
        if event in dcr.excludesTo:
            for e_prime in dcr.excludesTo[event]:
                dcr.marking.included.discard(e_prime)

        if event in dcr.includesTo:
            for e_prime in dcr.includesTo[event]:
                dcr.marking.included.add(e_prime)

        if event in dcr.responseTo:
            for e_prime in dcr.responseTo[event]:
                dcr.marking.pending.add(e_prime)

        return dcr

    @classmethod
    def is_accepting(cls, dcr) -> bool:
        res = dcr.marking.pending.intersection(dcr.marking.included)
        if len(res) > 0:
            return False
        else:
            return True

    @classmethod
    def is_execution_equivalent(cls, marking1: Marking, marking2: Marking) -> bool:
        return (
                marking1.executed == marking2.executed and
                marking1.included == marking2.included and
                marking1.pending == marking2.pending
        )

