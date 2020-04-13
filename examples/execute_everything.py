import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

if __name__ == "__main__":
    from examples import log_skeleton
    from examples import roles_detection
    from examples import alignment_test
    from examples import dec_treplay_imdf
    from examples import logs_petri_visual_comparison
    from examples import imdf_example
    from examples import test_evaluation
    from examples import token_replay_alpha
    from examples import manual_log_generation
    from examples import token_replay_imdf
    from examples import decisiontree_trivial_example
    from examples import decisiontree_align_example
    from examples import align_decomposition_example
    from examples import parquet
    from examples import sna_log
    from examples import transition_system_test
    from examples import heu_miner_test
    from examples import dfg_min_ex
    from examples import graphs_visualization
    from examples import big_dataframe_filtering
    from examples import big_dataframe_management
    from examples import backwards_token_replay
    from examples import transient_dfg
    from examples import transient_petri_net
    from examples import montecarlo_dfg
    from examples import montecarlo_petri_net

    print("\n\nlog_skeleton")
    log_skeleton.execute_script()
    print("\n\nroles_detection")
    roles_detection.execute_script()
    print("\n\nalignment_test")
    alignment_test.execute_script()
    print("\n\ndec_treplay_imdf")
    dec_treplay_imdf.execute_script()
    print("\n\nlogs_petri_visual_comparison")
    logs_petri_visual_comparison.execute_script()
    print("\n\nimdf_example")
    imdf_example.execute_script()
    print("\n\ntestEvaluation")
    test_evaluation.execute_script()
    print("\n\nsna_log")
    sna_log.execute_script()
    print("\n\ntokenReplay_alpha")
    token_replay_alpha.execute_script()
    print("\n\nmanual_log_generation")
    manual_log_generation.execute_script()
    print("\n\ntokenReplay_imdf")
    token_replay_imdf.execute_script()
    print("\n\ndecisiontree_trivial_example")
    decisiontree_trivial_example.execute_script()
    print("\n\ndecisiontree_align_example")
    decisiontree_align_example.execute_script()
    print("\n\nalign_decomposition_example")
    align_decomposition_example.execute_script()
    print("\n\ndfg_min_ex")
    dfg_min_ex.execute_script()
    print("\n\nparquet")
    parquet.execute_script()
    print("\n\ntransition_system_test")
    transition_system_test.execute_script()
    print("\n\nheu_miner_test")
    heu_miner_test.execute_script()
    print("\n\ngraphs_visualization")
    graphs_visualization.execute_script()
    print("\n\nbig_dataframe_management")
    big_dataframe_management.execute_script()
    print("\n\nbig_dataframe_filtering")
    big_dataframe_filtering.execute_script()
    print("\n\nbackwards_token_replay")
    backwards_token_replay.execute_script()
    print("\n\ntransient_dfg")
    transient_dfg.execute_script()
    print("\n\ntransient_petri_net")
    transient_petri_net.execute_script()
    print("\n\nmontecarlo_dfg")
    montecarlo_dfg.execute_script()
    print("\n\nmontecarlo_petri_net")
    montecarlo_petri_net.execute_script()
