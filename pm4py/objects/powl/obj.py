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
from typing import Optional, Union, List as TList


class POWL(ProcessTree):
    def __str__(self) -> str:
        return self.__repr__()

    def print(self) -> None:
        print(self.__repr__())

    def simplify_using_frequent_transitions(self) -> "POWL":
        return self

    def simplify(self) -> "POWL":
        return self

    def apply_all_reductions(self) -> "POWL":
        res = self.simplify()
        res = res.simplify_using_frequent_transitions()
        return res


class Transition(POWL):
    transition_id: int = 0

    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__()
        self._label = label
        self._identifier = Transition.transition_id
        Transition.transition_id = Transition.transition_id + 1

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


class FrequentTransition(Transition):
    def __init__(self, label, min_freq: Union[str, int], max_freq: Union[str, int]) -> None:
        self.min_freq = min_freq
        self.max_freq = max_freq
        if min_freq == 0 and max_freq == "-":
            suffix = "*"
        elif min_freq == 1 and max_freq == "-":
            suffix = "+"
        elif min_freq == 0 and max_freq == 1:
            suffix = "?"
        else:
            suffix = str(min_freq) + ", " + str(max_freq)
        super().__init__(label=label + "\n" + "[" + suffix + "]")


class StrictPartialOrder(POWL):

    def __init__(self, nodes: TList[POWL]) -> None:
        super().__init__()
        self.operator = Operator.PARTIALORDER
        self._set_order(nodes)
        self.additional_information = None

    def _set_order(self, nodes: TList[POWL]) -> None:
        self.order = BinaryRelation(nodes)

    def get_order(self) -> BinaryRelation:
        return self.order

    def _set_children(self, children: TList[POWL]) -> None:
        self.order.nodes = children

    def get_children(self) -> TList[POWL]:
        return self.order.nodes

    def __repr__(self) -> str:
        return STRICT_PARTIAL_ORDER_LABEL + self.order.__repr__()

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

        for node_1 in self.children:
            connected = False
            for node_2 in self.children:
                if self.partial_order.is_edge(node_1, node_2) or self.partial_order.is_edge(node_2, node_1):
                    connected = True
                    # break
            if not connected and isinstance(node_1, StrictPartialOrder):
                sub_nodes[node_1] = node_1.simplify()
            else:
                simplified_nodes[node_1] = node_1.simplify()

        new_nodes = list(simplified_nodes.values())
        for po, simplified_po in sub_nodes.items():
            new_nodes = new_nodes + list(simplified_po.children)
        res = StrictPartialOrder(new_nodes)
        for node_1 in self.children:
            for node_2 in self.children:
                if self.partial_order.is_edge(node_1, node_2):
                    res.partial_order.add_edge(simplified_nodes[node_1], simplified_nodes[node_2])
        for po, simplified_po in sub_nodes.items():
            for node_1 in simplified_po.children:
                for node_2 in simplified_po.children:
                    if simplified_po.partial_order.is_edge(node_1, node_2):
                        res.partial_order.add_edge(node_1, node_2)
        return res


class Sequence(StrictPartialOrder):

    def __init__(self, nodes: TList[POWL]) -> None:
        super().__init__(nodes)
        for i in range(len(nodes)):
            for j in range(i+1, len(nodes)):
                self.partial_order.add_edge(nodes[i], nodes[j])
        self.operator = Operator.SEQUENCE

    def _set_sequence(self, nodes: TList[POWL]) -> None:
        self._sequence: list[POWL] = nodes

    def get_sequence(self) -> TList[POWL]:
        return self._sequence

    def simplify(self) -> "Sequence":
        new_nodes = []
        for child in self.children:
            if isinstance(child, Sequence):
                for node in child.children:
                    new_nodes.append(node)
            else:
                new_nodes.append(child)
        return Sequence([child.simplify() for child in new_nodes])

    # def simplify_using_frequent_transitions(self):
    #     sequences = []
    #     last_activity = None
    #     counter = 0
    #     for child in self.children:
    #         if isinstance(child, Transition):
    #
    #             if last_activity is not None:
    #                 if child.label == last_activity:
    #                     counter = counter + 1
    #                 else:
    #                     if counter == 1:
    #                         sequences.append(Transition(label = last_activity))
    #                     counter = 1


class OperatorPOWL(POWL):
    def __init__(self, operator: Operator, children: TList[POWL]) -> None:
        super().__init__()
        self.operator = operator
        self.children = children

    def __lt__(self, other: object)-> bool:
        if isinstance(other, OperatorPOWL):
            return self.__repr__() < other.__repr__()
        elif isinstance(other, Transition):
            return False
        elif isinstance(other, StrictPartialOrder):
            return True
        return NotImplemented

    def equal_content(self, other: object)-> bool:
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
                if isinstance(child0, SilentTransition) and isinstance(child1,
                                                                       OperatorPOWL) and child1.operator is Operator.LOOP:
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
                if isinstance(child, OperatorPOWL) and child.operator is Operator.XOR:
                    for node in child.children:
                        new_children.append(node)
                else:
                    new_children.append(child)
            return OperatorPOWL(Operator.XOR, [child.simplify() for child in new_children])
        else:
            return OperatorPOWL(self.operator, [child.simplify() for child in self.children])
