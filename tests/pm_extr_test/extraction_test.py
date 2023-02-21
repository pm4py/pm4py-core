import inspect
import os
import sys
import traceback

if __name__ == "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    parentdir2 = os.path.dirname(parentdir)
    sys.path.insert(0, parentdir)
    sys.path.insert(0, parentdir2)
    import time

    from pm4py.objects.log.importer.xes import importer as xes_importer
    from pm4py.algo.discovery.inductive import algorithm as inductive
    from pm4py.algo.conformance.alignments.petri_net.variants import state_equation_a_star
    from pm4py.algo.discovery.footprints import algorithm as footprints_discovery
    from pm4py.algo.conformance.footprints import algorithm as footprints_conformance
    from pm4py.algo.discovery.alpha import algorithm as alpha
    from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
    from pm4py.objects.conversion.process_tree import converter as pt_converter
    from pm4py.algo.evaluation.replay_fitness import algorithm as fitness_evaluator
    from pm4py.algo.evaluation.precision import algorithm as precision_evaluator
    from pm4py.algo.evaluation.simplicity import algorithm as simplicity_evaluator
    from pm4py.algo.evaluation.generalization import algorithm as generalization_evaluator
    from pm4py.objects.log.util import insert_classifier
    from pm4py.objects.petri_net.exporter import exporter as pnml_exporter
    from pm4py.visualization.petri_net import visualizer as petri_vis
    from pm4py.visualization.common.save import save as vis_save
    from pm4py import util as pmutil
    from pm4py.algo.analysis.woflan import algorithm as woflan


    def get_elonged_string(stru):
        nchar = 30

        if len(stru) >= nchar:
            return stru

        return stru + " ".join([""] * (nchar - len(stru)))


    def get_elonged_float(value):
        stru = "%.3f" % value

        return get_elonged_string(stru)


    ENABLE_VISUALIZATIONS = False
    ENABLE_VISUALIZATIONS_INDUCTIVE = False
    ENABLE_ALIGNMENTS = False
    ENABLE_PRECISION = True
    ENABLE_PETRI_EXPORTING = False
    ENABLE_PETRI_EXPORTING_DEBUG = True
    CHECK_SOUNDNESS = True
    WOFLAN_RETURN_ASAP = True
    WOFLAN_PRINT_DIAGNOSTICS = True
    WOFLAN_RETURN_DIAGNOSTICS = True
    INDUCTIVE_MINER_VARIANT = inductive.Variants.IM_CLEAN
    ALIGN_VARIANT = state_equation_a_star
    logFolder = os.path.join("..", "compressed_input_data")
    pnmlFolder = "pnml_folder"
    pngFolder = "png_folder"
    times_tokenreplay_alpha = {}
    times_tokenreplay_imdf = {}
    times_footprints_imdf = {}
    times_alignments_imdf = {}
    fitness_token_alpha = {}
    fitness_token_imdf = {}
    fitness_footprints_imdf = {}
    fitness_align_imdf = {}
    precision_alpha = {}
    precision_imdf = {}
    simplicity_alpha = {}
    simplicity_imdf = {}
    generalization_alpha = {}
    generalization_imdf = {}


    def write_report():
        f = open("report.txt", "w")

        f.write("\n\n")
        f.write("Fitness on Alpha and Inductive models - measured by token-based replay and alignments\n")
        f.write("----\n")
        f.write(
            get_elonged_string("log") + "\t" + get_elonged_string("fitness_token_alpha") + "\t" + get_elonged_string(
                "times_tokenreplay_alpha") + "\t" + get_elonged_string(
                "fitness_token_imdf") + "\t" + get_elonged_string("times_tokenreplay_imdf") + "\t" + get_elonged_string(
                "fitness_footprints_imdf") + "\t" + get_elonged_string("times_footprints_imdf"))
        if ENABLE_ALIGNMENTS:
            f.write(
                "\t" + get_elonged_string("fitness_align_imdf") + "\t" + get_elonged_string("times_alignments_imdf"))
        f.write("\n")
        for this_logname in precision_alpha:
            # F.write("%s\t\t%.3f\t\t%.3f\n" % (logName, fitness_token_alpha[logName], fitness_token_imdf[logName]))
            f.write(get_elonged_string(this_logname))
            f.write("\t")
            f.write(get_elonged_float(fitness_token_alpha[this_logname]))
            f.write("\t")
            f.write(get_elonged_float(times_tokenreplay_alpha[this_logname]))
            f.write("\t")
            f.write(get_elonged_float(fitness_token_imdf[this_logname]))
            f.write("\t")
            f.write(get_elonged_float(times_tokenreplay_imdf[this_logname]))
            f.write("\t")
            f.write(get_elonged_float(fitness_footprints_imdf[this_logname]))
            f.write("\t")
            f.write(get_elonged_float(times_footprints_imdf[this_logname]))
            if ENABLE_ALIGNMENTS:
                f.write("\t")
                f.write(get_elonged_float(fitness_align_imdf[this_logname]))
                f.write("\t")
                f.write(get_elonged_float(times_alignments_imdf[this_logname]))
            f.write("\n")
        f.write("\n\n")
        f.write("Precision measured by ETConformance where activated transitions are retrieved using token replay\n")
        f.write("----\n")
        f.write(get_elonged_string("log") + "\t" + get_elonged_string("precision_alpha") + "\t" + get_elonged_string(
            "precision_imdf") + "\n")
        for this_logname in precision_alpha:
            f.write(get_elonged_string(this_logname))
            f.write("\t")
            f.write(get_elonged_float(precision_alpha[this_logname]))
            f.write("\t")
            f.write(get_elonged_float(precision_imdf[this_logname]))
            f.write("\n")
        f.write("\n\n")
        f.write("Generalization based on token replay transition recall\n")
        f.write("----\n")
        f.write(
            get_elonged_string("log") + "\t" + get_elonged_string("generalization_alpha") + "\t" + get_elonged_string(
                "generalization_imdf") + "\n")
        for this_logname in precision_alpha:
            f.write(get_elonged_string(this_logname))
            f.write("\t")
            f.write(get_elonged_float(generalization_alpha[this_logname]))
            f.write("\t")
            f.write(get_elonged_float(generalization_imdf[this_logname]))
            f.write("\n")
        f.write("\n\n")
        f.write("Simplicity based on inverse arc degree\n")
        f.write("----\n")
        f.write(get_elonged_string("log") + "\t" + get_elonged_string("simplicity_alpha") + "\t" + get_elonged_string(
            "simplicity_imdf") + "\n")
        for this_logname in precision_alpha:
            f.write(get_elonged_string(this_logname))
            f.write("\t")
            f.write(get_elonged_float(simplicity_alpha[this_logname]))
            f.write("\t")
            f.write(get_elonged_float(simplicity_imdf[this_logname]))
            f.write("\n")
        f.write("\n")
        f.close()


    for logName in os.listdir(logFolder):
        if "." in logName:
            logNamePrefix = logName.split(".")[0]
            logExtension = logName[len(logNamePrefix) + 1:]

            print("\nelaborating " + logName)

            logPath = os.path.join(logFolder, logName)
            if "xes" in logExtension:
                log = xes_importer.apply(logPath, variant=xes_importer.Variants.CHUNK_REGEX)

            log, classifier_key = insert_classifier.search_act_class_attr(log, force_activity_transition_insertion=True)

            print("loaded log")

            activity_key = "concept:name"
            if classifier_key is not None:
                activity_key = classifier_key

            parameters_discovery = {pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key,
                                    pmutil.constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: activity_key}
            t1 = time.time()
            alpha_model, alpha_initial_marking, alpha_final_marking = alpha.apply(log, parameters=parameters_discovery)
            if ENABLE_PETRI_EXPORTING:
                pnml_exporter.export_net(alpha_model, alpha_initial_marking,
                                         os.path.join(pnmlFolder, logNamePrefix + "_alpha.pnml"),
                                         final_marking=alpha_final_marking)
            t2 = time.time()
            print("time interlapsed for calculating Alpha Model", (t2 - t1))
            if CHECK_SOUNDNESS:
                try:
                    res_woflan, diagn = woflan.apply(alpha_model, alpha_initial_marking, alpha_final_marking,
                                              parameters={"return_asap_when_not_sound": WOFLAN_RETURN_ASAP,
                                                          "print_diagnostics": WOFLAN_PRINT_DIAGNOSTICS,
                                                          "return_diagnostics": WOFLAN_RETURN_DIAGNOSTICS})
                    print("alpha woflan", res_woflan)
                except:
                    if ENABLE_PETRI_EXPORTING_DEBUG:
                        exce = traceback.format_exc()
                        pnml_exporter.export_net(alpha_model, alpha_initial_marking,
                                                 os.path.join(pnmlFolder, logNamePrefix + "_alpha.pnml"),
                                                 final_marking=alpha_final_marking)
                        F = open(logNamePrefix + "_alpha.txt", "w")
                        F.write(exce)
                        F.close()
            t1 = time.time()
            heu_model, heu_initial_marking, heu_final_marking = heuristics_miner.apply(log,
                                                                                       parameters=parameters_discovery)
            if ENABLE_PETRI_EXPORTING:
                pnml_exporter.export_net(heu_model, heu_initial_marking,
                                         os.path.join(pnmlFolder, logNamePrefix + "_heuristics.pnml"),
                                         final_marking=heu_final_marking)
            t2 = time.time()
            print("time interlapsed for calculating Heuristics Model", (t2 - t1))
            if CHECK_SOUNDNESS:
                try:
                    res_woflan, diagn = woflan.apply(heu_model, heu_initial_marking, heu_initial_marking,
                                              parameters={"return_asap_when_not_sound": WOFLAN_RETURN_ASAP,
                                                          "print_diagnostics": WOFLAN_PRINT_DIAGNOSTICS,
                                                          "return_diagnostics": WOFLAN_RETURN_DIAGNOSTICS})
                    print("heuristics woflan", res_woflan)
                except:
                    if ENABLE_PETRI_EXPORTING_DEBUG:
                        exce = traceback.format_exc()
                        pnml_exporter.export_net(heu_model, heu_initial_marking,
                                                 os.path.join(pnmlFolder, logNamePrefix + "_heuristics.pnml"),
                                                 final_marking=heu_final_marking)
                        F = open(logNamePrefix + "_heuristics.txt", "w")
                        F.write(exce)
                        F.close()

            t1 = time.time()
            tree = inductive.apply(log, parameters=parameters_discovery, variant=INDUCTIVE_MINER_VARIANT)
            # print(tree)

            inductive_model, inductive_im, inductive_fm = pt_converter.apply(tree,
                                                                             variant=pt_converter.Variants.TO_PETRI_NET)

            """inductive_model, inductive_im, inductive_fm = inductive.apply(log, parameters=parameters_discovery,
                                                                          variant=INDUCTIVE_MINER_VARIANT)"""
            if ENABLE_PETRI_EXPORTING:
                pnml_exporter.export_net(inductive_model, inductive_im,
                                         os.path.join(pnmlFolder, logNamePrefix + "_inductive.pnml"),
                                         final_marking=inductive_fm)
            """
            generated_log = pt_semantics.generate_log(tree)
            print("first trace of log", [x["concept:name"] for x in generated_log[0]])
            """
            t2 = time.time()
            print("time interlapsed for calculating Inductive Model", (t2 - t1))
            if CHECK_SOUNDNESS:
                res_woflan, diagn = woflan.apply(inductive_model, inductive_im, inductive_fm,
                                          parameters={"return_asap_when_not_sound": WOFLAN_RETURN_ASAP,
                                                          "print_diagnostics": WOFLAN_PRINT_DIAGNOSTICS,
                                                          "return_diagnostics": WOFLAN_RETURN_DIAGNOSTICS})
                print("inductive woflan", res_woflan)

            parameters = {fitness_evaluator.Variants.TOKEN_BASED.value.Parameters.ACTIVITY_KEY: activity_key,
                          fitness_evaluator.Variants.TOKEN_BASED.value.Parameters.ATTRIBUTE_KEY: activity_key,
                          "align_variant": ALIGN_VARIANT,
                          "format": "png"}

            t1 = time.time()
            fitness_token_alpha[logName] = \
                fitness_evaluator.apply(log, alpha_model, alpha_initial_marking, alpha_final_marking,
                                        parameters=parameters, variant=fitness_evaluator.Variants.TOKEN_BASED)[
                    'perc_fit_traces']
            print(str(time.time()) + " fitness_token_alpha for " + logName + " succeeded! " + str(
                fitness_token_alpha[logName]))
            t2 = time.time()
            times_tokenreplay_alpha[logName] = t2 - t1

            t1 = time.time()
            fitness_token_imdf[logName] = \
                fitness_evaluator.apply(log, inductive_model, inductive_im, inductive_fm, parameters=parameters,
                                        variant=fitness_evaluator.Variants.TOKEN_BASED)[
                    'perc_fit_traces']
            print(str(time.time()) + " fitness_token_inductive for " + logName + " succeeded! " + str(
                fitness_token_imdf[logName]))
            t2 = time.time()
            times_tokenreplay_imdf[logName] = t2 - t1

            t1 = time.time()
            fp_log = footprints_discovery.apply(log, parameters=parameters)
            fp_tree = footprints_discovery.apply(tree, parameters=parameters)
            conf = footprints_conformance.apply(fp_log, fp_tree,
                                                variant=footprints_conformance.Variants.TRACE_EXTENSIVE,
                                                parameters=parameters)
            # fitness_fp = float(len([x for x in conf if len(x) == 0])) / float(len(conf)) * 100.0 if conf else 0.0
            fitness_fp = float(len([x for x in conf if x["is_footprints_fit"]])) / float(
                len(conf)) * 100.0 if conf else 0.0
            t2 = time.time()
            fitness_footprints_imdf[logName] = fitness_fp
            times_footprints_imdf[logName] = t2 - t1

            if ENABLE_ALIGNMENTS:
                t1 = time.time()
                fitness_align_imdf[logName] = \
                    fitness_evaluator.apply(log, inductive_model, inductive_im, inductive_fm,
                                            variant=fitness_evaluator.Variants.ALIGNMENT_BASED, parameters=parameters)[
                        'percFitTraces']
                print(str(time.time()) + " fitness_token_align for " + logName + " succeeded! " + str(
                    fitness_align_imdf[logName]))
                t2 = time.time()
                times_alignments_imdf[logName] = t2 - t1

            if ENABLE_PRECISION:
                precision_alpha[logName] = precision_evaluator.apply(log, alpha_model, alpha_initial_marking,
                                                                     alpha_final_marking,
                                                                     variant=precision_evaluator.Variants.ETCONFORMANCE_TOKEN,
                                                                     parameters=parameters)
            else:
                precision_alpha[logName] = 0.0
            print(str(time.time()) + " precision_alpha for " + logName + " succeeded! " + str(precision_alpha[logName]))

            generalization_alpha[logName] = generalization_evaluator.apply(log, alpha_model, alpha_initial_marking,
                                                                           alpha_final_marking, parameters=parameters)
            print(str(time.time()) + " generalization_alpha for " + logName + " succeeded! " + str(
                generalization_alpha[logName]))
            simplicity_alpha[logName] = simplicity_evaluator.apply(alpha_model, parameters=parameters)
            print(
                str(time.time()) + " simplicity_alpha for " + logName + " succeeded! " + str(simplicity_alpha[logName]))

            if ENABLE_PRECISION:
                precision_imdf[logName] = precision_evaluator.apply(log, inductive_model, inductive_im,
                                                                    inductive_fm,
                                                                    variant=precision_evaluator.Variants.ETCONFORMANCE_TOKEN,
                                                                    parameters=parameters)
            else:
                precision_imdf[logName] = 0.0
            print(str(time.time()) + " precision_imdf for " + logName + " succeeded! " + str(precision_imdf[logName]))

            generalization_imdf[logName] = generalization_evaluator.apply(log, inductive_model, inductive_im,
                                                                          inductive_fm, parameters=parameters)
            print(str(time.time()) + " generalization_imdf for " + logName + " succeeded! " + str(
                generalization_imdf[logName]))
            simplicity_imdf[logName] = simplicity_evaluator.apply(inductive_model, parameters=parameters)
            print(str(time.time()) + " simplicity_imdf for " + logName + " succeeded! " + str(simplicity_imdf[logName]))

            write_report()

            if ENABLE_VISUALIZATIONS:
                try:
                    alpha_vis = petri_vis.apply(alpha_model, alpha_initial_marking, alpha_final_marking, log=log,
                                                parameters=parameters, variant=petri_vis.Variants.FREQUENCY)
                    vis_save(alpha_vis, os.path.join(pngFolder, logNamePrefix + "_alpha.png"))
                    print(str(time.time()) + " alpha visualization for " + logName + " succeeded!")
                except:
                    print(str(time.time()) + " alpha visualization for " + logName + " failed!")
                    traceback.print_exc()

                try:
                    heuristics_vis = petri_vis.apply(heu_model, heu_initial_marking, heu_final_marking,
                                                     log=log, parameters=parameters,
                                                     variant=petri_vis.FREQUENCY_DECORATION)
                    vis_save(heuristics_vis, os.path.join(pngFolder, logNamePrefix + "_heuristics.png"))
                    print(str(time.time()) + " heuristics visualization for " + logName + " succeeded!")
                except:
                    print(str(time.time()) + " heuristics visualization for " + logName + " failed!")
                    traceback.print_exc()

            if ENABLE_VISUALIZATIONS or ENABLE_VISUALIZATIONS_INDUCTIVE:
                try:
                    inductive_vis = petri_vis.apply(inductive_model, inductive_im, inductive_fm,
                                                    log=log, parameters=parameters,
                                                    variant=petri_vis.PERFORMANCE_DECORATION)
                    vis_save(inductive_vis, os.path.join(pngFolder, logNamePrefix + "_inductive.png"))
                    print(str(time.time()) + " inductive visualization for " + logName + " succeeded!")
                except:
                    print(str(time.time()) + " inductive visualization for " + logName + " failed!")
                    traceback.print_exc()
