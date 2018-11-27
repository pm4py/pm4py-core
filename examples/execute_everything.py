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
    from examples import token_replay_imdf
    from examples import decisiontree_example
    from examples import clustering_example
    from examples import big_dataframe_filtering
    from examples import big_dataframe_management

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
    print("\n\ntokenReplay_alpha")
    token_replay_alpha.execute_script()
    print("\n\ntokenReplay_imdf")
    token_replay_imdf.execute_script()
    print("\n\ndecisiontree_example")
    decisiontree_example.execute_script()
    print("\n\nclustering_example")
    clustering_example.execute_script()
    print("\n\nbig_dataframe_filtering")
    big_dataframe_filtering.execute_script()
    print("\n\nbig_dataframe_management")
    big_dataframe_management.execute_script()
