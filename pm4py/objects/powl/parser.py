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
from pm4py.objects.powl.obj import POWL, OperatorPOWL, StrictPartialOrder, SilentTransition, Transition
from pm4py.objects.process_tree.obj import Operator as PTOperator
from pm4py.util import hie_utils
import re


def parse_powl_model_string(powl_string, level=0) -> POWL:
    """
    Parse a POWL model from a string representation of the process model
    (with the same format as the __repr__ and __str__ methods of the POWL model)

    Minimum Viable Example:

        from pm4py.objects.powl.parser import parse_powl_model_string

        powl_model = parse_powl_model_string('PO=(nodes={ NODE1, NODE2, NODE3 }, order={ NODE1-->NODE2 }')
        print(powl_model)


    Parameters
    ------------------
    powl_string
        POWL model expressed as a string (__repr__ of the POWL model)

    Returns
    ------------------
    powl_model
        POWL model
    """
    powl_string = powl_string.replace('\n', '').replace('\r', '').replace('\t', '').strip()
    max_indent = 1
    if powl_string.startswith('PO=') or powl_string.startswith('PO('):
        max_indent = 2
    if powl_string.startswith("'"):
        max_indent = 0

    indented_str_list = hie_utils.indent_representation(powl_string, max_indent=max_indent)

    indented_str_list = [x.strip() for x in indented_str_list]
    indented_str_list = [x[:-1] if x and x[-1] == ',' else x for x in indented_str_list]
    PO = None
    nodes = []

    if indented_str_list:
        if indented_str_list[0].startswith('PO=') or indented_str_list[0].startswith('PO('):
            nodes_dict = {}

            # read the nodes of the POWL
            i = 2
            while i < len(indented_str_list):
                if indented_str_list[i] == '}':
                    break
                N = parse_powl_model_string(indented_str_list[i], level + 1)
                nodes_dict[indented_str_list[i]] = N
                nodes.append(N)
                i = i + 1

            pattern = '(' + '|'.join(map(re.escape, list(nodes_dict))) + ')'

            PO = StrictPartialOrder(nodes=nodes)

            # reads the edges of the POWL
            i = i + 2
            while i < len(indented_str_list):
                if indented_str_list[i] == '}':
                    break

                split_list = [x for x in re.split(pattern, indented_str_list[i]) if x]

                if len(split_list) == 3:
                    PO.order.add_edge(nodes_dict[split_list[0]], nodes_dict[split_list[2]])

                i = i + 1

        elif indented_str_list[0].startswith('X'):
            i = 1
            while i < len(indented_str_list):
                if indented_str_list[i] == ')':
                    break
                N = parse_powl_model_string(indented_str_list[i], level + 1)
                nodes.append(N)
                i = i + 1
            PO = OperatorPOWL(PTOperator.XOR, nodes)
        elif indented_str_list[0].startswith('*'):
            i = 1
            while i < len(indented_str_list):
                if indented_str_list[i] == ')':
                    break
                N = parse_powl_model_string(indented_str_list[i], level + 1)
                nodes.append(N)
                i = i + 1
            PO = OperatorPOWL(PTOperator.LOOP, nodes)
        elif indented_str_list[0].startswith('tau'):
            PO = SilentTransition()
        else:
            label = indented_str_list[0]
            if label.startswith("'"):
                label = label[1:-1]
            PO = Transition(label=label)

    return PO
