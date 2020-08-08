import inspect
import os
import sys
import traceback


def tree_playout():
    from examples import tree_playout
    print("\n\ntree_playout")
    tree_playout.execute_script()


def emd_evaluation():
    from examples import emd_evaluation
    print("\n\nemd_evaluation")
    emd_evaluation.execute_script()


def footprints_tree_conf():
    from examples import footprints_tree_conf
    print("\n\nfootprints_tree_conf")
    footprints_tree_conf.execute_script()


def simplified_interface():
    from examples import simplified_interface
    print("\n\nsimplified_interface")
    simplified_interface.execute_script()


def footprints_petri_net():
    from examples import footprints_petri_net
    print("\n\nfootprints_petri_net")
    footprints_petri_net.execute_script()


def events_log_filter():
    from examples import event_log_filter
    print("\n\nevent_log_filter")
    event_log_filter.execute_script()


def event_log_map():
    from examples import event_log_map
    print("\n\nevent_log_map")
    event_log_map.execute_script()


def event_stream_filter():
    from examples import event_stream_filter
    print("\n\nevent_stream_filter")
    event_stream_filter.execute_script()


def event_stream_map():
    from examples import event_stream_map
    print("\n\nevent_stream_map")
    event_stream_map.execute_script()


def corr_mining():
    from examples import corr_mining
    print("\n\ncorr_mining")
    corr_mining.execute_script()


def log_skeleton():
    from examples import log_skeleton
    print("\n\nlog_skeleton")
    log_skeleton.execute_script()


def roles_detection():
    from examples import roles_detection
    print("\n\nroles_detection")
    roles_detection.execute_script()


def alignment_test():
    from examples import alignment_test
    print("\n\nalignment_test")
    alignment_test.execute_script()


def dec_treplay_imdf():
    from examples import dec_treplay_imdf
    print("\n\ndec_treplay_imdf")
    dec_treplay_imdf.execute_script()


def logs_petri_visual_comparison():
    from examples import logs_petri_visual_comparison
    print("\n\nlogs_petri_visual_comparison")
    logs_petri_visual_comparison.execute_script()


def imdf_example():
    from examples import imdf_example
    print("\n\nimdf_example")
    imdf_example.execute_script()


def test_evaluation():
    from examples import test_evaluation
    print("\n\ntestEvaluation")
    test_evaluation.execute_script()


def sna_log():
    from examples import sna_log
    print("\n\nsna_log")
    sna_log.execute_script()


def token_replay_alpha():
    from examples import token_replay_alpha
    print("\n\ntokenReplay_alpha")
    token_replay_alpha.execute_script()


def manual_log_generation():
    from examples import manual_log_generation
    print("\n\nmanual_log_generation")
    manual_log_generation.execute_script()


def token_replay_imdf():
    from examples import token_replay_imdf
    print("\n\ntokenReplay_imdf")
    token_replay_imdf.execute_script()


def decisiontree_trivial_example():
    from examples import decisiontree_trivial_example
    print("\n\ndecisiontree_trivial_example")
    decisiontree_trivial_example.execute_script()


def decisiontree_align_example():
    from examples import decisiontree_align_example
    print("\n\ndecisiontree_align_example")
    decisiontree_align_example.execute_script()


def align_decomposition_example():
    from examples import align_decomposition_example
    print("\n\nalign_decomposition_example")
    align_decomposition_example.execute_script()


def transition_system_test():
    from examples import transition_system_test
    print("\n\ntransition_system_test")
    transition_system_test.execute_script()


def heu_miner_test():
    from examples import heu_miner_test
    print("\n\nheu_miner_test")
    heu_miner_test.execute_script()


def dfg_min_ex():
    from examples import dfg_min_ex
    print("\n\ndfg_min_ex")
    dfg_min_ex.execute_script()


def graphs_visualization():
    from examples import graphs_visualization
    print("\n\ngraphs_visualization")
    graphs_visualization.execute_script()


def backwards_token_replay():
    from examples import backwards_token_replay
    print("\n\nbackwards_token_replay")
    backwards_token_replay.execute_script()


def transient_dfg():
    from examples import transient_dfg
    print("\n\ntransient_dfg")
    transient_dfg.execute_script()


def transient_petri_net():
    from examples import transient_petri_net
    print("\n\ntransient_petri_net")
    transient_petri_net.execute_script()


def monte_carlo_dfg():
    from examples import montecarlo_dfg
    print("\n\nmontecarlo_dfg")
    montecarlo_dfg.execute_script()


def monte_carlo_petri_net():
    from examples import montecarlo_petri_net
    print("\n\nmontecarlo_petri_net")
    montecarlo_petri_net.execute_script()


def visualization_processtree():
    from examples import visualization_processtree
    print("\n\nvisualization_processtree")
    visualization_processtree.execute_script()


def visualization_align_table():
    from examples import visualization_align_table
    print("\n\nvisualization_align_table")
    visualization_align_table.execute_script()


def execute_script(f):
    try:
        f()
    except:
        traceback.print_exc()
        input("\npress INPUT if you want to continue")


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

if __name__ == "__main__":
    execute_script(tree_playout)
    execute_script(emd_evaluation)
    execute_script(footprints_tree_conf)
    execute_script(simplified_interface)
    execute_script(footprints_petri_net)
    execute_script(events_log_filter)
    execute_script(event_log_map)
    execute_script(event_stream_filter)
    execute_script(event_stream_map)
    execute_script(corr_mining)
    execute_script(log_skeleton)
    execute_script(roles_detection)
    execute_script(alignment_test)
    execute_script(dec_treplay_imdf)
    execute_script(logs_petri_visual_comparison)
    execute_script(imdf_example)
    execute_script(test_evaluation)
    execute_script(sna_log)
    execute_script(token_replay_alpha)
    execute_script(manual_log_generation)
    execute_script(token_replay_imdf)
    execute_script(decisiontree_trivial_example)
    execute_script(decisiontree_align_example)
    execute_script(align_decomposition_example)
    execute_script(transition_system_test)
    execute_script(heu_miner_test)
    execute_script(dfg_min_ex)
    execute_script(graphs_visualization)
    execute_script(backwards_token_replay)
    execute_script(transient_dfg)
    execute_script(transient_petri_net)
    execute_script(monte_carlo_dfg)
    execute_script(monte_carlo_petri_net)
    execute_script(visualization_processtree)
    execute_script(visualization_align_table)
