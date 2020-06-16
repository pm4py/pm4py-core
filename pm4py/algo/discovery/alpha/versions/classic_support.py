import pm4py.algo.discovery.alpha.versions.classic as alpha_classic

from typing import TypeVar,List
from multiprocessing import Pool
from os import cpu_count
from math import ceil

ClassicAlphaAbstraction = TypeVar('ClassicAlphaAbstraction')
Key = TypeVar('Key')
Value = TypeVar('Value')

def find_alpha_pair(
    left_pair:tuple,
    right_pairs:List[tuple],
    parallel_relation:List[tuple],
    causal_relation:List[tuple],
    alpha_parallel_relation_starts:List[Key],
    alpha_causal_relation_starts:List[Key],
    alpha_parallel_relation_ends:List[Value],
    alpha_causal_relation_ends:List[Value]
    ) -> List[tuple]:
    """
    find_alpha_pair
    ----------------
    Creates alpha pairs for the Alpha Miner (classic) based on the give relations,
    left side and a collection of possible right pairs

    Parameters
    ------------
    left_pair\n
        \tConsidered left pair (tuple)\n
    right_pairs\n
        \tPossible joins for left_pair (list of tuples)\n
    parallel_relation\n
        \tList of tuples from ClassicAlphaAbstraction.parallel_relation\n
    causal_relation\n
        \tList of tuples from ClassicAlphaAbstraction.causal_relation\n
    alpha_parallel_relation_[starts([0])/ends([1])]\n
        \tList of key/values from ClassicAlphaAbstraction.parallel_relation\n
    alpha_causal_relation_[starts([0])/ends([1])]\n
        \tList of key/values from ClassicAlphaAbstraction.causal_relation\n

    Returns
    -------
    new_rights :: List of tuples\n
        \tA new list of possible pair combinations to be added to pairs, not filtered
    """
    new_pairs = []
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
                                new_pairs.append(
                                     (left_pair[0] | right_pair[0], left_pair[1] | right_pair[1])
                                )
    return new_pairs

def run_batch_alpha_pairs(
    t1:tuple,
    pairs:List[tuple],
    alpha_abstraction:ClassicAlphaAbstraction,
    ) -> List[tuple] :
        """
        run_batch_alpha_pairs
        -----------
        Generates new set of alpha pairs by paritioning work over a process pool of workers (CPU_CORES - 1 of machine)
        then returns the new alpha pairs list for the next iteration of focused left pair (t1).

        Parameters
        ------------
        t1 :: tuple\n
            \tThe current focused `left_pair` to join on\n
        pairs :: List[tuple]\n
            \tThe current set of alpha pairs from iterations to attempt to join t1 to.
        alpha_abstraction :: ClassicAlphaAbstraction\n
            \tThe data structure abstraction for this selection of traces.

        Returns
        --------
        pairs :: List[tuple]\n
            \t A new list of unique alpha pairs ready for the next iteration of left pair (t1).
        """
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