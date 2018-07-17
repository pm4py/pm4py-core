from itertools import zip_longest

from pm4py.algo.alpha import data_structures as ds


def apply(trace_log):
    alpha_abstraction = ds.ClassicAlphaAbstraction(trace_log)
    pairs = list(map(lambda p: ({p[0]}, {p[1]}), filter(lambda p: __initial_filter(alpha_abstraction.parallel_relation, p), alpha_abstraction.causal_relation)))

    for i in range(0, len(pairs)):
        t1 = pairs[i]
        for j in range(i, len(pairs)):
            t2 = pairs[j]
            if t1 != t2:
                if t1[0].issubset(t2[0]) or t1[1].issubset(t2[1]):
                    if not (__check_is_unrelated(alpha_abstraction.parallel_relation, alpha_abstraction.causal_relation,
                                                 t1[0], t2[0]) or __check_is_unrelated(
                            alpha_abstraction.parallel_relation, alpha_abstraction.causal_relation, t1[1], t2[1])):
                        new_alpha_pair = (t1[0] | t2[0], t1[1] | t2[1])
                        if new_alpha_pair not in pairs:
                            pairs.append((t1[0] | t2[0], t1[1] | t2[1]))
                            break
    return filter(lambda p: __pair_maximizer(pairs, p), pairs)


def __initial_filter(parallel_relation, pair):
    if (pair[0], pair[0]) in parallel_relation or (pair[1], pair[1]) in parallel_relation:
        return False
    return True


def __pair_maximizer(alpha_pairs, pair):
    for alt in alpha_pairs:
        if pair != alt and pair[0].issubset(alt[0]) and pair[1].issubset(alt[1]):
            return False
    return True


def __check_is_unrelated(parallel_relation, causal_relation, item_set_1, item_set_2):
    for pair in zip_longest(item_set_1, item_set_2):
        if pair in parallel_relation or pair in causal_relation:
            return True
    return False
