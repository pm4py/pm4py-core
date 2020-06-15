import pm4py.algo.discovery.alpha.versions.classic as alpha_classic

def find_alpha_pair(
    left_pair:tuple,
    right_pair:tuple,
    parallel_relation:list,
    causal_relation:list,
    alpha_parallel_relation_starts:list,
    alpha_causal_relation_starts:list,
    alpha_parallel_relation_ends:list,
    alpha_causal_relation_ends:list
    ) -> tuple:

    if left_pair[0].issubset(right_pair[0]) or left_pair[1].issubset(right_pair[1]):
                    if not (
                            alpha_classic.__check_is_unrelated(
                        parallel_relation, causal_relation,
                        left_pair[0], right_pair[0],
                        alpha_parallel_relation_starts,alpha_causal_relation_starts,
                        alpha_parallel_relation_ends,alpha_causal_relation_ends) 
                        or
                              alpha_classic.__check_is_unrelated(
                        parallel_relation, causal_relation,
                        left_pair[1], right_pair[1],
                        alpha_parallel_relation_starts,alpha_causal_relation_starts,
                        alpha_parallel_relation_ends,alpha_causal_relation_ends)
                        ):
                            return (left_pair[0] | right_pair[0], left_pair[1] | right_pair[1])