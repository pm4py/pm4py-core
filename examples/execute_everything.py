import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

if __name__ == "__main__":
    from examples import big_log_imdf_decor
    from examples import alignment_test
    from examples import dec_treplay_imdf
    from examples import imdf_example
    from examples import test_evaluation
    from examples import token_replay_alpha
    from examples import manual_log_generation
    from examples import simple_miner
    from examples import example_simulation
    from examples import token_replay_imdf
    from examples import decisiontree_example
    from examples import example_diagnostics
    from examples import parquet
    from examples import sna_log
    from examples import transition_system_test
    from examples import heu_miner_test
    from examples import stochastic_petri_nets
    from examples import stochastic_petri_df
    from examples import dfg_min_ex
    from examples import big_dataframe_filtering
    from examples import big_dataframe_management
    from examples import graphs_visualization

    print("\n\nbig_log_imdf_decor frequency")
    big_log_imdf_decor.execute_script(variant="frequency")
    print("\n\nbig_log_imdf_decor performance")
    big_log_imdf_decor.execute_script(variant="performance")
    print("\n\nalignment_test")
    alignment_test.execute_script()
    print("\n\ndec_treplay_imdf")
    dec_treplay_imdf.execute_script()
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
    print("\n\ndecisiontree_example")
    decisiontree_example.execute_script()
    print("\n\nexample_diagnostics")
    example_diagnostics.execute_script()
    print("\n\ndfg_min_ex")
    dfg_min_ex.execute_script()
    print("\n\nparquet")
    parquet.execute_script()
    print("\n\ntransition_system_test")
    transition_system_test.execute_script()
    print("\n\nheu_miner_test")
    heu_miner_test.execute_script()
    print("\n\nstochastic_petri_nets")
    stochastic_petri_nets.execute_script()
    print("\n\nstochastic_petri_df")
    stochastic_petri_df.execute_script()
    print("\n\nbig_dataframe_filtering")
    big_dataframe_filtering.execute_script()
    print("\n\nbig_dataframe_management")
    big_dataframe_management.execute_script()
    print("\n\nsimple_miner")
    simple_miner.execute_script()
    print("\n\nexample_simulation")
    example_simulation.execute_script()
    print("\n\ngraphs_visualization")
    graphs_visualization.execute_script()
