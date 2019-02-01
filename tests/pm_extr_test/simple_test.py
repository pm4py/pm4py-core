import inspect
import os
import sys

if __name__ == "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    parentdir2 = os.path.dirname(parentdir)
    sys.path.insert(0, parentdir)
    sys.path.insert(0, parentdir2)
    from pm4py.objects.log.importer.xes import factory as xes_factory
    from pm4py.objects.petri.exporter import pnml as pnml_exporter
    from pm4py.visualization.petrinet import factory as petri_vis_factory
    from pm4py.algo.discovery.simple.model.log import factory as simple_model_factory

    logFolder = os.path.join("..", "compressed_input_data")
    pnmlFolder = "simple_pnml"
    pngFolder = "simple_png"

    for logName in os.listdir(logFolder):
        if "." in logName:
            logNamePrefix = logName.split(".")[0]

            print("\nelaborating " + logName)

            logPath = os.path.join(logFolder, logName)
            log = xes_factory.import_log(logPath, variant="iterparse")

            net, initial_marking, final_marking = simple_model_factory.apply(log, classic_output=True)

            pnml_exporter.export_net(net, initial_marking, os.path.join(pnmlFolder, logNamePrefix) + ".pnml",
                                     final_marking=final_marking)

            gviz = petri_vis_factory.apply(net, initial_marking, final_marking, log=log, variant="frequency")

            petri_vis_factory.save(gviz, os.path.join(pngFolder, logNamePrefix) + ".png")
