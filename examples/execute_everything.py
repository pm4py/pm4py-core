import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import examples.alignment_test
import examples.big_dataframe_filtering
import examples.big_dataframe_management
import examples.big_log_imdf_decor
import examples.dec_treplay_imdf
import examples.dfgExample
import examples.imdf_example
import examples.simple_visualization
import examples.testEvaluation
import examples.testPetriGenerator
import examples.tokenReplay_alpha
import examples.tokenReplay_imdf
import examples.transition_system_test

print("\n\nalignment_test")
examples.alignment_test.execute_script()
print("\n\nbig_dataframe_filtering")
examples.big_dataframe_filtering.execute_script()
print("\n\nbig_dataframe_management")
examples.big_dataframe_management.execute_script()
print("\n\nbig_log_imdf_decor")
examples.big_log_imdf_decor.execute_script()
print("\n\ndec_treplay_imdf")
examples.dec_treplay_imdf.execute_script()
print("\n\ndfgExample")
examples.dfgExample.execute_script()
print("\n\nimdf_example")
examples.imdf_example.execute_script()
print("\n\nsimple_visualization")
examples.simple_visualization.execute_script()
print("\n\ntestEvaluation")
examples.testEvaluation.execute_script()
print("\n\ntestPetriGenerator")
examples.testPetriGenerator.execute_script()
print("\n\ntokenReplay_alpha")
examples.tokenReplay_alpha.execute_script()
print("\n\ntokenReplay_imdf")
examples.tokenReplay_imdf.execute_script()
print("\n\ntransition_system_test")
examples.transition_system_test.execute_script()