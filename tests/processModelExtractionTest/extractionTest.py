import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentdir2 = os.path.dirname(parentdir)
sys.path.insert(0,parentdir)
sys.path.insert(0,parentdir2)
import time
from pm4py.entities.log.importer.xes import factory as xes_factory
from pm4py.algo.discovery.inductive import factory as inductive
from pm4py.algo.discovery.alpha import factory as alpha
from pm4py.evaluation.replay_fitness import factory as fitness_factory
from pm4py.evaluation.precision import factory as precision_factory
from pm4py.evaluation.simplicity import factory as simplicity_factory
from pm4py.evaluation.generalization import factory as generalization_factory
from pm4py.entities.log.util import insert_classifier
from pm4py.entities.petri.exporter import pnml as pnml_exporter
from pm4py.visualization.petrinet import factory as petri_vis_factory
from pm4py.visualization.common.save import save as vis_save
from pm4py import util as pmutil

if __name__ == "__main__":
    def get_elonged_string(stru):
        NCHAR = 30

        if len(stru) >= NCHAR:
            return stru

        return stru + " ".join([""] * (NCHAR - len(stru)))


    def get_elonged_float(value):
        stru = "%.3f" % (value)

        return get_elonged_string(stru)

    ENABLE_ALIGNMENTS = False
    logFolder = "..\\compressedInputData"
    pnmlFolder = "pnmlFolder"
    pngFolder = "pngFolder"
    times_tokenreplay_alpha = {}
    times_tokenreplay_imdf = {}
    times_alignments_imdf = {}
    fitness_token_alpha = {}
    fitness_token_imdf = {}
    fitness_align_imdf = {}
    precision_alpha = {}
    precision_imdf = {}
    simplicity_alpha = {}
    simplicity_imdf = {}
    generalization_alpha = {}
    generalization_imdf = {}


    def write_report():
        F = open("report.txt", "w")

        F.write("\n\n")
        F.write("Fitness on Alpha and Inductive models - measured by token-based replay and alignments\n")
        F.write("----\n")
        F.write(get_elonged_string("log") + "\t" + get_elonged_string("fitness_token_alpha") + "\t" + get_elonged_string(
                "times_tokenreplay_alpha") + "\t" + get_elonged_string(
                "fitness_token_imdf") + "\t" + get_elonged_string("times_tokenreplay_imdf"))
        if ENABLE_ALIGNMENTS:
            F.write("\t" + get_elonged_string("fitness_align_imdf") + "\t" + get_elonged_string("times_alignments_imdf"))
        F.write("\n")
        for logName in precision_alpha:
            # F.write("%s\t\t%.3f\t\t%.3f\n" % (logName, fitness_token_alpha[logName], fitness_token_imdf[logName]))
            F.write(get_elonged_string(logName))
            F.write("\t")
            F.write(get_elonged_float(fitness_token_alpha[logName]))
            F.write("\t")
            F.write(get_elonged_float(times_tokenreplay_alpha[logName]))
            F.write("\t")
            F.write(get_elonged_float(fitness_token_imdf[logName]))
            F.write("\t")
            F.write(get_elonged_float(times_tokenreplay_imdf[logName]))
            if ENABLE_ALIGNMENTS:
                F.write("\t")
                F.write(get_elonged_float(fitness_align_imdf[logName]))
                F.write("\t")
                F.write(get_elonged_float(times_alignments_imdf[logName]))
            F.write("\n")
        F.write("\n\n")
        F.write("Precision measured by ETConformance where activated transitions are retrieved using token replay\n")
        F.write("----\n")
        F.write(get_elonged_string("log") + "\t" + get_elonged_string("precision_alpha") + "\t" + get_elonged_string(
            "precision_imdf") + "\n")
        for logName in precision_alpha:
            F.write(get_elonged_string(logName))
            F.write("\t")
            F.write(get_elonged_float(precision_alpha[logName]))
            F.write("\t")
            F.write(get_elonged_float(precision_imdf[logName]))
            F.write("\n")
        F.write("\n\n")
        F.write("Generalization based on token replay transition recall\n")
        F.write("----\n")
        F.write(
            get_elonged_string("log") + "\t" + get_elonged_string("generalization_alpha") + "\t" + get_elonged_string(
                "generalization_imdf") + "\n")
        for logName in precision_alpha:
            F.write(get_elonged_string(logName))
            F.write("\t")
            F.write(get_elonged_float(generalization_alpha[logName]))
            F.write("\t")
            F.write(get_elonged_float(generalization_imdf[logName]))
            F.write("\n")
        F.write("\n\n")
        F.write("Simplicity based on inverse arc degree\n")
        F.write("----\n")
        F.write(get_elonged_string("log") + "\t" + get_elonged_string("simplicity_alpha") + "\t" + get_elonged_string(
            "simplicity_imdf") + "\n")
        for logName in precision_alpha:
            F.write(get_elonged_string(logName))
            F.write("\t")
            F.write(get_elonged_float(simplicity_alpha[logName]))
            F.write("\t")
            F.write(get_elonged_float(simplicity_imdf[logName]))
            F.write("\n")
        F.write("\n")
        F.close()

    for logName in os.listdir(logFolder):
        if "." in logName:
            logNamePrefix = logName.split(".")[0]

            print("\nelaborating "+logName)

            logPath = os.path.join(logFolder, logName)
            log = xes_factory.import_log(logPath, variant="iterparse")

            log, classifier_key = insert_classifier.search_and_insert_event_classifier_attribute(log)

            print("loaded log")

            activity_key = "concept:name"
            if not classifier_key is None:
                activity_key = classifier_key

            parameters_discovery = {pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}
            t1 = time.time()
            alpha_model, alpha_initial_marking, alpha_final_marking = alpha.apply(log, parameters=parameters_discovery)
            pnml_exporter.export_net(alpha_model, alpha_initial_marking, os.path.join(pnmlFolder, logNamePrefix + "_alpha.pnml"))
            t2 = time.time()
            print("time interlapsed for calculating Alpha Model",(t2-t1))

            t1 = time.time()
            inductive_model, inductive_initial_marking, inductive_final_marking = inductive.apply(log, parameters=parameters_discovery)
            pnml_exporter.export_net(inductive_model, inductive_initial_marking, os.path.join(pnmlFolder, logNamePrefix + "_inductive.pnml"))
            t2 = time.time()
            print("time interlapsed for calculating Inductive Model",(t2-t1))

            parameters = {"activity_key":activity_key, "format":"png"}

            alpha_vis = petri_vis_factory.apply(alpha_model, alpha_initial_marking, alpha_final_marking, log=log, parameters=parameters, variant="frequency")
            vis_save(alpha_vis, os.path.join(pngFolder, logNamePrefix + "_alpha.png"))
            inductive_vis = petri_vis_factory.apply(inductive_model, inductive_initial_marking, inductive_final_marking, log=log, parameters=parameters, variant="frequency")
            vis_save(inductive_vis, os.path.join(pngFolder, logNamePrefix + "_inductive.png"))

            t1 = time.time()
            fitness_token_alpha[logName] = fitness_factory.apply(log, alpha_model, alpha_initial_marking, alpha_final_marking, parameters=parameters)['percFitTraces']
            t2 = time.time()
            times_tokenreplay_alpha[logName] = t2 - t1

            t1 = time.time()
            fitness_token_imdf[logName] = fitness_factory.apply(log, inductive_model, inductive_initial_marking, inductive_final_marking, parameters=parameters)['percFitTraces']
            t2 = time.time()
            times_tokenreplay_imdf[logName] = t2 - t1



            if ENABLE_ALIGNMENTS:
                t1 = time.time()
                fitness_align_imdf[logName] = fitness_factory.apply(log, inductive_model, inductive_initial_marking, inductive_final_marking, variant="alignments", parameters=parameters)['percFitTraces']
                t2 = time.time()
                times_alignments_imdf[logName] = t2 - t1

            precision_alpha[logName] = precision_factory.apply(log, alpha_model, alpha_initial_marking, alpha_final_marking, parameters=parameters)
            generalization_alpha[logName] = generalization_factory.apply(log, alpha_model, alpha_initial_marking, alpha_final_marking, parameters=parameters)
            simplicity_alpha[logName] = simplicity_factory.apply(alpha_model, parameters=parameters)

            precision_imdf[logName] = precision_factory.apply(log, inductive_model, inductive_initial_marking, inductive_final_marking, parameters=parameters)
            generalization_imdf[logName] = generalization_factory.apply(log, inductive_model, inductive_initial_marking, inductive_final_marking, parameters=parameters)
            simplicity_imdf[logName] = simplicity_factory.apply(inductive_model, parameters=parameters)

            write_report()