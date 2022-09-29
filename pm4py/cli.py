import pm4py
import sys
import os
import itertools
from pathlib import Path
import traceback
import pandas as pd


methods = {
    "ConvertToXES": {"inputs": [".csv"], "output_extension": ".xes",
                          "method": lambda x: pm4py.write_xes(
                              pm4py.convert_to_event_log(pm4py.format_dataframe(pd.read_csv(x[0]))), x[1])},
    "ConvertToCSV": {"inputs": [".xes"], "output_extension": ".csv",
                     "method": lambda x: pm4py.convert_to_dataframe(pm4py.read_xes(x[0])).to_csv(x[1], index=False)},
    "ConvertPNMLtoBPMN": {"inputs": [".pnml"], "output_extension": ".bpmn",
                           "method": lambda x: pm4py.write_bpmn(pm4py.convert_to_bpmn(*pm4py.read_pnml(x[0])), x[1])},
    "ConvertPNMLtoPTML": {"inputs": [".pnml"], "output_extension": ".ptml",
                          "method": lambda x: pm4py.write_ptml(pm4py.convert_to_process_tree(*pm4py.read_pnml(x[0])), x[1])},
    "ConvertPTMLtoPNML": {"inputs": [".ptml"], "output_extension": ".pnml",
                          "method": lambda x: pm4py.write_pnml(*pm4py.convert_to_petri_net(pm4py.read_ptml(x[0])), x[1])},
    "ConvertPTMLtoBPMN": {"inputs": [".ptml"], "output_extension": ".bpmn",
                          "method": lambda x: pm4py.write_bpmn(pm4py.convert_to_bpmn(pm4py.read_ptml(x[0])), x[1])},
    "ConvertBPMNtoPNML": {"inputs": [".bpmn"], "output_extension": ".pnml",
                          "method": lambda x: pm4py.write_pnml(*pm4py.convert_to_petri_net(pm4py.read_bpmn(x[0])), x[1])},
    "ConvertDFGtoPNML": {"inputs": [".dfg"], "output_extension": ".pnml",
                         "method": lambda x: pm4py.write_pnml(*pm4py.convert_to_petri_net(*pm4py.read_dfg(x[0])), x[1])},
    "DiscoverPetriNetAlpha": {"inputs": [".xes"], "output_extension": ".pnml",
                              "method": lambda x: pm4py.write_pnml(*pm4py.discover_petri_net_alpha(read_log(x[0])),
                                                                   x[1])},
    "DiscoverPetriNetInductive": {"inputs": [".xes"], "output_extension": ".pnml",
                                  "method": lambda x: pm4py.write_pnml(
                                      *pm4py.discover_petri_net_inductive(read_log(x[0])),
                                      x[1])},
    "DiscoverPetriNetHeuristics": {"inputs": [".xes"], "output_extension": ".pnml",
                                   "method": lambda x: pm4py.write_pnml(
                                       *pm4py.discover_petri_net_heuristics(read_log(x[0])),
                                       x[1])},
    "DiscoverBPMNInductive": {"inputs": [".xes"], "output_extension": ".bpmn",
                              "method": lambda x: pm4py.write_bpmn(
                                  pm4py.discover_bpmn_inductive(read_log(x[0])),
                                  x[1])},
    "DiscoverProcessTreeInductive": {"inputs": [".xes"], "output_extension": ".ptml",
                              "method": lambda x: pm4py.write_ptml(
                                  pm4py.discover_process_tree_inductive(read_log(x[0])),
                                  x[1])},
    "DiscoverDFG": {"inputs": [".xes"], "output_extension": ".dfg",
                    "method": lambda x: pm4py.write_dfg(*pm4py.discover_dfg(read_log(x[0])), x[1])},
    "ConformanceDiagnosticsTBR": {"inputs": [".xes", ".pnml"], "output_extension": ".txt",
                                  "method": lambda x: open(x[2], "w").write(str(
                                      pm4py.conformance_diagnostics_token_based_replay(read_log(x[0]),
                                                                                       *pm4py.read_pnml(x[1]))))},
    "ConformanceDiagnosticsAlignments": {"inputs": [".xes", ".pnml"], "output_extension": ".txt",
                                  "method": lambda x: open(x[2], "w").write(str(
                                      pm4py.conformance_diagnostics_alignments(read_log(x[0]),
                                                                                       *pm4py.read_pnml(x[1]))))},
    "FitnessTBR": {"inputs": [".xes", ".pnml"], "output_extension": ".txt",
                                  "method": lambda x: open(x[2], "w").write(str(
                                      pm4py.fitness_token_based_replay(read_log(x[0]),
                                                                                       *pm4py.read_pnml(x[1]))))},
    "FitnessAlignments": {"inputs": [".xes", ".pnml"], "output_extension": ".txt",
                                         "method": lambda x: open(x[2], "w").write(str(
                                             pm4py.fitness_alignments(read_log(x[0]),
                                                                                      *pm4py.read_pnml(x[1]))))},
    "PrecisionTBR": {"inputs": [".xes", ".pnml"], "output_extension": ".txt",
                   "method": lambda x: open(x[2], "w").write(str(
                       pm4py.precision_token_based_replay(read_log(x[0]),
                                                        *pm4py.read_pnml(x[1]))))},
    "PrecisionAlignments": {"inputs": [".xes", ".pnml"], "output_extension": ".txt",
                          "method": lambda x: open(x[2], "w").write(str(
                              pm4py.precision_alignments(read_log(x[0]),
                                                       *pm4py.read_pnml(x[1]))))},
    "SaveVisDFG": {"inputs": [".dfg"], "output_extension": ".png",
                   "method": lambda x: pm4py.save_vis_dfg(*pm4py.read_dfg(x[0]), x[1])},
    "SaveVisPNML": {"inputs": [".pnml"], "output_extension": ".png",
                    "method": lambda x: pm4py.save_vis_petri_net(*pm4py.read_pnml(x[0]), x[1])},
    "SaveVisBPMN": {"inputs": [".bpmn"], "output_extension": ".png",
                    "method": lambda x: pm4py.save_vis_bpmn(pm4py.read_bpmn(x[0]), x[1])},
    "SaveVisPTML": {"inputs": [".ptml"], "output_extension": ".png",
                    "method": lambda x: pm4py.save_vis_process_tree(pm4py.read_ptml(x[0]), x[1])},
    "SaveVisDottedChart": {"inputs": [".xes", None, None, None], "output_extension": ".png",
                           "method": lambda x: pm4py.save_vis_dotted_chart(read_log(x[0]), x[4], attributes=[x[1], x[2], x[3]])},
    "SaveVisTransitionSystem": {"inputs": [".xes"], "output_extension": ".png",
                                "method": lambda x: pm4py.save_vis_transition_system(pm4py.discover_transition_system(read_log(x[0])), x[1])},
    "SaveVisTrie": {"inputs": [".xes"], "output_extension": ".png", "method": lambda x: pm4py.save_vis_prefix_tree(pm4py.discover_prefix_tree(read_log(x[0])), x[1])},
    "SaveVisEventsDistribution": {"inputs": [".xes", None], "output_extension": ".png", "method": lambda x: pm4py.save_vis_events_distribution_graph(read_log(x[0]), x[2], distr_type=x[1])},
    "SaveVisEventsPerTime": {"inputs": [".xes"], "output_extension": ".png", "method": lambda x: pm4py.save_vis_events_per_time_graph(read_log(x[0]), x[1])}
}


def read_log(log_path):
    if "xes" in log_path.lower():
        return pm4py.read_xes(log_path)
    elif "csv" in log_path.lower():
        dataframe = pd.read_csv(log_path)
        dataframe = pm4py.format_dataframe(dataframe)
        return dataframe


def __get_output_name(inp_list, idx, method_name, extension):
    ret = []
    for inp in inp_list:
        ret.append(str(Path(inp).stem))
    return "_".join(ret) + "_" + method_name + extension


def cli_interface():
    method_name = sys.argv[1]
    if method_name in methods:
        method = methods[method_name]
        inputs = []
        for i in range(len(method["inputs"])):
            ci = sys.argv[2 + i]
            if os.path.isdir(ci):
                if not os.path.exists(ci):
                    raise Exception("the provided path (" + ci + ") does not exist.")
                files = os.listdir(ci)
                inputs.append([os.path.join(ci, f) for f in files if
                               os.path.isfile(os.path.join(ci, f)) and f.endswith(method["inputs"][i])])
            else:
                inputs.append([ci])
        j = 2 + len(method["inputs"])
        inputs = list(itertools.product(*inputs))
        if len(inputs) == 1:
            outputs = [[sys.argv[j]]]
        else:
            if not os.path.exists(sys.argv[j]):
                os.mkdir(sys.argv[j])
            outputs = [[os.path.join(sys.argv[j], __get_output_name(inputs[z], z, method_name, method["output_extension"]))] for z in
                       range(len(inputs))]
        method_tuples = [(*inputs[i], *outputs[i]) for i in range(len(inputs))]
        for i in range(len(method_tuples)):
            try:
                if not os.path.exists(method_tuples[i][-1]):
                    print(method_name, method_tuples[i])
                    method["method"](method_tuples[i])
            except:
                traceback.print_exc()
    else:
        raise Exception("the provided method ("+method_name+") does not exist in the CLI.")


if __name__ == "__main__":
    cli_interface()
