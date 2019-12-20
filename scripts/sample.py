from pm4py.objects.log.importer.xes import factory as xes_log_importer
from pm4py.algo.conformance.alignments import factory as alignment_algorithm
from pm4py.objects.petri.importer import factory as pn_importer

'''
Use the scripts folder to write custom scripts for your (research) project, when using PM4Py directly from source.  
'''


def py_data_2019_demo_script():
    event_data = xes_log_importer.apply('<path_to_data>')
    model, marking_i, marking_f = pn_importer.apply('<path_to_model>')
    alignments = alignment_algorithm.apply(event_data, model, marking_i, marking_f)
    print(alignments)


if __name__ == '__main__':
    py_data_2019_demo_script()
