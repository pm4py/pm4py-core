'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''

from pm4py.objects.powl.BinaryRelation import BinaryRelation
from pm4py.objects.powl.constants import STRICT_PARTIAL_ORDER_LABEL
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.util import hie_utils
import sys
from typing import List as TList, Optional, Union
from abc import ABC, abstractmethod



class POWL(ProcessTree, ABC):
    def print(self) -> None:
        print(self.to_string())

    def simplify_using_frequent_transitions(self) -> "POWL":
        return self

    def simplify(self) -> "POWL":
        return self

    def validate_partial_orders(self):
        if isinstance(self, StrictPartialOrder):
            if not self.order.is_irreflexive():
                raise Exception("The irreflexivity of the partial order is violated!")
            if not self.order.is_transitive():
                raise Exception("The transitivity of the partial order is violated!")
        if hasattr(self, 'children'):
            for child in self.children:
                child.validate_partial_orders()

    @staticmethod
    def model_description() -> str:
        descr = """A partially ordered workflow language (POWL) is a partially ordered graph representation of a process, extended with control-flow operators for modeling choice and loop structures. There are four types of POWL models:
- an activity (identified by its label, i.e., 'M' identifies the activity M). Silent activities with empty labels (tau labels) are also supported.
- a choice of other POWL models (an exclusive choice between the sub-models A and B is identified by X ( A, B ) )
- a loop node between two POWL models (a loop between the sub-models A and B is identified by * ( A, B ) and tells that you execute A, then you either exit the loop or execute B and then A again, this is repeated until you exit the loop).
- a partial order over a set of POWL models. A partial order is a binary relation that is irreflexive, transitive, and asymmetric. A partial order sets an execution order between the sub-models (i.e., the target node cannot be executed before the source node is completed). Unconnected nodes in a partial order are considered to be concurrent. An example is PO=(nodes={ NODE1, NODE2 }, order={ })
where NODE1 and NODE2 are independent and can be executed in parallel. Another example is PO=(nodes={ NODE1, NODE2 }, order={ NODE1-->NODE2 }) where NODE2 can only be executed after NODE1 is completed.

A more advanced example: PO=(nodes={ NODE1, NODE2, NODE3, X ( NODE4, NODE5 ) }, order={ NODE1-->NODE2, NODE1-->X ( NODE4, NODE5 ), NODE2-->X ( NODE4, NODE5 ) }), in this case, NODE2 can be executed only after NODE1 is completed, while the choice between NODE4 and NODE5 needs to wait until both NODE1 and NODE2 are finalized.


"""
        return descr

    @abstractmethod
    def copy(self):
        pass


class Transition(POWL):
    transition_id: int = 0

    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__()
        self._label = label
        self._identifier = Transition.transition_id
        Transition.transition_id = Transition.transition_id + 1

    def copy(self):
        return Transition(self._label)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Transition):
            return self._label == other._label and self._identifier == other._identifier
        return False

    def equal_content(self, other: object) -> bool:
        if isinstance(other, Transition):
            return self._label == other._label
        return False

    def __hash__(self) -> int:
        return self._identifier

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Transition):
            if self.label and other.label and self.label < other.label:
                return self.label < other.label
            return self._identifier < other._identifier
        elif isinstance(other, OperatorPOWL):
            return True
        elif isinstance(other, StrictPartialOrder):
            return True
        return NotImplemented


class SilentTransition(Transition):
    def __init__(self) -> None:
        super().__init__(label=None)

    def copy(self):
        return SilentTransition()


class FrequentTransition(Transition):
    def __init__(self, label, min_freq: Union[str, int], max_freq: Union[str, int]) -> None:
        self.skippable = False
        self.selfloop = False
        if min_freq == 0:
            self.skippable = True
        if max_freq == "-":
            self.selfloop = True
        min_freq = "1"
        self.activity = label
        if self.skippable or self.selfloop:
            label = str(label) + "\n" + "[" + str(min_freq) + "," + str(max_freq) + "]"

        super().__init__(label=label)


class StrictPartialOrder(POWL):

    def __init__(self, nodes: TList[POWL]) -> None:
        super().__init__()
        self.operator = Operator.PARTIALORDER
        self._set_order(nodes)
        self.additional_information = None

    def copy(self):
        copied_nodes = {n:n.copy() for n in self.order.nodes}
        res = StrictPartialOrder(list(copied_nodes.values()))
        for n1 in self.order.nodes:
            for n2 in self.order.nodes:
                if self.order.is_edge(n1, n2):
                    res.add_edge(copied_nodes[n1], copied_nodes[n2])
        return res


    def _set_order(self, nodes: TList[POWL]) -> None:
        self.order = BinaryRelation(nodes)

    def get_order(self) -> BinaryRelation:
        return self.order

    def _set_children(self, children: TList[POWL]) -> None:
        self.order.nodes = children

    def get_children(self) -> TList[POWL]:
        return self.order.nodes

    def to_string(self, level=0, indent=False, max_indent=sys.maxsize) -> str:
        model_string = STRICT_PARTIAL_ORDER_LABEL + self.order.__repr__()
        if indent:
            model_string = "\n".join(hie_utils.indent_representation(model_string, max_indent=max_indent))
        return model_string

    def __repr__(self) -> str:
        return self.to_string()

    def __lt__(self, other: object) -> bool:
        if isinstance(other, StrictPartialOrder):
            return self.__repr__() < other.__repr__()
        elif isinstance(other, OperatorPOWL):
            return False
        elif isinstance(other, Transition):
            return False
        return NotImplemented

    partial_order = property(get_order, _set_order)
    children = property(get_children, _set_children)

    # def __eq__(self, other):
    #     if not isinstance(other, StrictPartialOrder):
    #         return False
    #
    #     ordered_nodes_1 = sorted(list(self.order.nodes))
    #     ordered_nodes_2 = sorted(list(other.order.nodes))
    #     if len(ordered_nodes_1) != len(ordered_nodes_2):
    #         return False
    #     for i in range(len(ordered_nodes_1)):
    #         source_1 = ordered_nodes_1[i]
    #         source_2 = ordered_nodes_2[i]
    #         if not source_1.__eq__(source_2):
    #             return False
    #         for j in range(len(ordered_nodes_1)):
    #             target_1 = ordered_nodes_1[j]
    #             target_2 = ordered_nodes_2[j]
    #             if self.order.is_edge(source_1, target_1) and not other.order.is_edge(source_2, target_2):
    #                 return False
    #             if not self.order.is_edge(source_1, target_1) and other.order.is_edge(source_2, target_2):
    #                 return False
    #     return True

    def equal_content(self, other: object) -> bool:
        if not isinstance(other, StrictPartialOrder):
            return False

        ordered_nodes_1 = sorted(list(self.order.nodes))
        ordered_nodes_2 = sorted(list(other.order.nodes))
        if len(ordered_nodes_1) != len(ordered_nodes_2):
            return False
        for i in range(len(ordered_nodes_1)):
            source_1 = ordered_nodes_1[i]
            source_2 = ordered_nodes_2[i]
            if not source_1.equal_content(source_2):
                return False
            for j in range(len(ordered_nodes_1)):
                target_1 = ordered_nodes_1[j]
                target_2 = ordered_nodes_2[j]
                if self.order.is_edge(source_1, target_1) and not other.order.is_edge(source_2, target_2):
                    return False
                if not self.order.is_edge(source_1, target_1) and other.order.is_edge(source_2, target_2):
                    return False
        return True

    def simplify_using_frequent_transitions(self) -> "StrictPartialOrder":
        new_nodes = {node: node.simplify_using_frequent_transitions() for node in self.children}
        res = StrictPartialOrder(list(new_nodes.values()))
        for node_1 in self.children:
            for node_2 in self.children:
                if self.partial_order.is_edge(node_1, node_2):
                    res.partial_order.add_edge(new_nodes[node_1], new_nodes[node_2])

        return res

    def simplify(self) -> "StrictPartialOrder":
        simplified_nodes = {}
        sub_nodes = {}
        start_nodes = {}
        end_nodes = {}

        def connected(node):
            for node2 in self.children:
                if self.partial_order.is_edge(node, node2) or self.partial_order.is_edge(node2, node):
                    return True
            return False

        for node_1 in self.children:
            simplified_node = node_1.simplify()
            if isinstance(simplified_node, StrictPartialOrder):

                if not connected(node_1):
                    sub_nodes[node_1] = simplified_node
                else:
                    s_nodes = simplified_node.order.get_start_nodes()
                    e_nodes = simplified_node.order.get_end_nodes()
                    if len(s_nodes) == 1 and len(e_nodes) == 1:
                        sub_nodes[node_1] = simplified_node
                        start_nodes[node_1] = list(s_nodes)[0]
                        end_nodes[node_1] = list(e_nodes)[0]
                    else:
                        simplified_nodes[node_1] = simplified_node
            else:
                simplified_nodes[node_1] = simplified_node

        new_nodes = list(simplified_nodes.values())
        for po, simplified_po in sub_nodes.items():
            new_nodes = new_nodes + list(simplified_po.children)
        res = StrictPartialOrder(new_nodes)
        for node_1 in self.children:
            for node_2 in self.children:
                if self.partial_order.is_edge(node_1, node_2):
                    if node_1 in simplified_nodes.keys() and node_2 in simplified_nodes.keys():
                        res.partial_order.add_edge(simplified_nodes[node_1], simplified_nodes[node_2])
                    elif node_1 in simplified_nodes.keys():
                        res.partial_order.add_edge(simplified_nodes[node_1], start_nodes[node_2])
                    elif node_2 in simplified_nodes.keys():
                        res.partial_order.add_edge(end_nodes[node_1], simplified_nodes[node_2])
                    else:
                        res.partial_order.add_edge(end_nodes[node_1], start_nodes[node_2])
        for po, simplified_po in sub_nodes.items():
            for node_1 in simplified_po.children:
                for node_2 in simplified_po.children:
                    if simplified_po.partial_order.is_edge(node_1, node_2):
                        res.partial_order.add_edge(node_1, node_2)
        return res

    def add_edge(self, source, target):
        return self.order.add_edge(source, target)


class Sequence(StrictPartialOrder):

    def __init__(self, nodes: TList[POWL]) -> None:
        super().__init__(nodes)
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                self.partial_order.add_edge(nodes[i], nodes[j])


class OperatorPOWL(POWL):
    def __init__(self, operator: Operator, children: TList[POWL]) -> None:
        if operator is Operator.XOR:
            if len(children) < 2:
                raise Exception("Cannot create a choice of less than 2 submodels!")
        elif operator is Operator.LOOP:
            if len(children) != 2:
                raise Exception("Only loops of length 2 are supported!")
        else:
            raise Exception("Unsupported Operator!")
        super().__init__()
        self.operator = operator
        self.children = children

    def copy(self):
        copied_nodes = [n.copy() for n in self.children]
        return OperatorPOWL(self.operator, copied_nodes)

    def __lt__(self, other: object) -> bool:
        if isinstance(other, OperatorPOWL):
            return self.__repr__() < other.__repr__()
        elif isinstance(other, Transition):
            return False
        elif isinstance(other, StrictPartialOrder):
            return True
        return NotImplemented

    def equal_content(self, other: object) -> bool:
        if not isinstance(other, OperatorPOWL):
            return False

        if self.operator != other.operator:
            return False

        ordered_nodes_1 = sorted(list(self.children))
        ordered_nodes_2 = sorted(list(other.children))
        if len(ordered_nodes_1) != len(ordered_nodes_2):
            return False
        for i in range(len(ordered_nodes_1)):
            node_1 = ordered_nodes_1[i]
            node_2 = ordered_nodes_2[i]
            if not node_1.equal_content(node_2):
                return False
        return True

    def simplify_using_frequent_transitions(self) -> POWL:
        if self.operator is Operator.XOR and len(self.children) == 2:
            child_0 = self.children[0]
            child_1 = self.children[1]
            if isinstance(child_0, Transition) and isinstance(child_1, SilentTransition):
                return FrequentTransition(label=child_0.label, min_freq=0, max_freq=1)
            elif isinstance(child_1, Transition) and isinstance(child_0, SilentTransition):
                return FrequentTransition(label=child_1.label, min_freq=0, max_freq=1)

        if self.operator is Operator.LOOP and len(self.children) == 2:
            child_0 = self.children[0]
            child_1 = self.children[1]
            if isinstance(child_0, Transition) and isinstance(child_1, SilentTransition):
                return FrequentTransition(label=child_0.label, min_freq=1, max_freq="-")
            elif isinstance(child_1, Transition) and isinstance(child_0, SilentTransition):
                return FrequentTransition(label=child_1.label, min_freq=0, max_freq="-")

        return OperatorPOWL(self.operator, [child.simplify_using_frequent_transitions() for child in self.children])

    def simplify(self) -> "OperatorPOWL":
        if self.operator is Operator.XOR and len(self.children) == 2:
            child_0 = self.children[0]
            child_1 = self.children[1]

            def merge_with_children(child0, child1):
                if isinstance(child0, SilentTransition) and isinstance(child1, OperatorPOWL) \
                        and child1.operator is Operator.LOOP:
                    if isinstance(child1.children[0], SilentTransition):
                        return OperatorPOWL(Operator.LOOP, [n.simplify() for n in child1.children])
                    elif isinstance(child1.children[1], SilentTransition):
                        return OperatorPOWL(Operator.LOOP, list(reversed([n.simplify() for n in child1.children])))

                return None

            res = merge_with_children(child_0, child_1)
            if res is not None:
                return res

            res = merge_with_children(child_1, child_0)
            if res is not None:
                return res

        if self.operator is Operator.XOR:
            new_children = []
            for child in self.children:
                s_child = child.simplify()
                if isinstance(s_child, OperatorPOWL) and s_child.operator is Operator.XOR:
                    for node in s_child.children:
                        new_children.append(node.simplify())
                else:
                    new_children.append(s_child)
            return OperatorPOWL(Operator.XOR, [child for child in new_children])
        else:
            return OperatorPOWL(self.operator, [child.simplify() for child in self.children])
