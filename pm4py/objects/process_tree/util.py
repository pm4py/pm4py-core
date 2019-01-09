from pm4py.objects.process_tree import state as pt_st
from pm4py.objects.process_tree import pt_operator as pt_op
from pm4py.objects.process_tree import process_tree as pt

def project_execution_sequence_to_leafs(execution_sequence):
    return list(map(lambda x: x[0], filter(lambda x: (x[1] is pt_st.State.OPEN and len(x[0].children) == 0), execution_sequence)))


def project_execution_sequence_to_labels(execution_sequence):
    return list(map(lambda x: x.label, filter(lambda x: x.label is not None, project_execution_sequence_to_leafs(execution_sequence))))

def parse(string_rep):
    depth_cache = dict()
    depth = 0
    return parse_recursive(string_rep,depth_cache,depth)


def parse_recursive(string_rep, depth_cache, depth):
    string_rep = string_rep.strip()
    node = None
    operator = None
    if string_rep.startswith(pt_op.Operator2.LOOP.value):
        operator = pt_op.Operator2.LOOP
        string_rep = string_rep[1:]
    elif string_rep.startswith(pt_op.Operator2.PARALLEL.value):
        operator = pt_op.Operator2.PARALLEL
        string_rep = string_rep[1:]
    elif string_rep.startswith(pt_op.Operator2.XOR.value):
        operator = pt_op.Operator2.XOR
        string_rep = string_rep[1:]
    elif string_rep.startswith(pt_op.Operator2.SEQUENCE.value):
        operator = pt_op.Operator2.SEQUENCE
        string_rep = string_rep[2:]
    if operator is not None:
        parent = None if depth == 0 else depth_cache[depth - 1]
        node = pt.ProcessTree2(operator=operator, parent=parent)
        depth_cache[depth] = node
        if parent is not None:
            parent.children.append(node)
        depth += 1
        string_rep = string_rep.strip()
        assert (string_rep[0] == '(')
        parse_recursive(string_rep[1:], depth_cache, depth)
    else:
        label = None
        if string_rep.startswith('\''):
            string_rep = string_rep[1:]
            escape_ext = string_rep.find('\'')
            label = string_rep[0:escape_ext]
            string_rep = string_rep[escape_ext+1:]
        else:
            assert(string_rep.startswith('tau'))
            string_rep = string_rep[3:]
        parent = None if depth == 0 else depth_cache[depth - 1]
        node = pt.ProcessTree2(operator=operator, parent=parent, label=label)
        if parent is not None:
            parent.children.append(node)

        while string_rep.strip().startswith(')'):
            depth -= 1
            string_rep = (string_rep.strip())[1:]
        if len(string_rep.strip()) > 0:
            parse_recursive((string_rep.strip())[1:], depth_cache, depth)
    return node
