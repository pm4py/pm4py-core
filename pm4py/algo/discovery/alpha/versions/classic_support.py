import pm4py.algo.discovery.alpha.versions.classic as alpha_classic

from typing import TypeVar
from multiprocessing import Pool
from os import cpu_count
from math import ceil

ClassicAlphaAbstraction = TypeVar('ClassicAlphaAbstraction')

def find_alpha_pair(
    left_pair:tuple,
    right_pairs:list,
    parallel_relation:list,
    causal_relation:list,
    alpha_parallel_relation_starts:list,
    alpha_causal_relation_starts:list,
    alpha_parallel_relation_ends:list,
    alpha_causal_relation_ends:list
    ) -> list:

    new_rights = []
    for right_pair in right_pairs:
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
                                new_rights.append(
                                     (left_pair[0] | right_pair[0], left_pair[1] | right_pair[1])
                                )
    return new_rights

def run_batch_alpha_pairs(
    t1:tuple,
    pairs:list,
    alpha_abstraction:ClassicAlphaAbstraction,
    ) -> list :
        # make starts and ends for relations
        alpha_parallel_relation_starts = [
        start 
        for start,end
        in alpha_abstraction.parallel_relation
        ]
        alpha_parallel_relation_ends = [
            end 
            for start,end
            in alpha_abstraction.parallel_relation
        ]
        alpha_causal_relation_starts = [
            start 
            for start,end
            in alpha_abstraction.causal_relation
        ]
        alpha_causal_relation_ends = [
            end 
            for start,end
            in alpha_abstraction.causal_relation
        ]
        #setup workers and begin processing
        with Pool(processes=cpu_count()-1) as p:
                #create new potential rights
                new_rights =  [ t2 
                            for t2 in pairs 
                            if t2 != None
                            if (t1[0] | t2[0], t1[1] | t2[1]) not in pairs
                            and t1 != t2 
                        ]
                #batch new rights for workers
                batch_size = ceil(len(new_rights)/(cpu_count()-1))
                new_rights = [
                    new_rights[start:end]
                    for start,end
                    in zip(
                        range(0,len(new_rights)+batch_size,batch_size),
                        range(50,len(new_rights)+batch_size*2,batch_size)
                    )
                ]
                #put workers to work on finding alpha pairs
                new_pairs = p.starmap(
                    find_alpha_pair,
                    [
                        (t1,t2,
                        alpha_abstraction.parallel_relation,alpha_abstraction.causal_relation,
                        alpha_parallel_relation_starts,alpha_causal_relation_starts,
                        alpha_parallel_relation_ends,alpha_causal_relation_ends)
                        for t2 
                        in new_rights
                    ]
                )
                #unpack results from workers
                new_pairs = [
                    pair 
                    for result 
                    in new_pairs
                    for pair 
                    in result
                ]
        #add unseen alpha pairs to pairs
        for new_pair in new_pairs:
            if new_pair not in pairs and new_pair != None:
                pairs.append(new_pair)
        return pairs