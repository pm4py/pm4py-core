import pm4py
import os
def execute_discover():
    """
    example script to discover dcr graph from event log
    """

    log = pm4py.read_xes(os.path.join("..","tests","input_data","running-example.xes"))

    #return the graph and the log abstraction used for mining
    graph, _ = pm4py.discover_dcr(log)
    print(graph)

def execute_discover_roles():
    """
    example script to discover dcr graph with orginazational information
    """
    log = pm4py.read_xes(os.path.join("..","tests","input_data","running-example.xes"))
    # is initaitad with the set of wanted post process types after the original discover miner
    # if no standard default group key is present, but org:resource is present, can specify
    graph, _ = pm4py.discover_dcr(log, process_type={'roles'}, group_key='org:resource')
    print(graph)

def execute_dcr_conformance():
    """
    example script of how to call and check for conformance of dcr graph
    """
    log = pm4py.read_xes(os.path.join("..","tests","input_data","receipt.xes"))

    # is initaitad with the set of wanted post process types after the original discover miner
    # if no standard default group key is present, but org:resource is present, can specify to mine org:resource as roles
    graph_base, _ = pm4py.discover_dcr(log)
    graph_roles, _ = pm4py.discover_dcr(log, process_type={'roles'})

    #DisCoveR discovers a perfect fitting graph from event log
    conf_res_base = pm4py.conformance_dcr(log, graph_base, return_diagnostics_dataframe=True)
    print(conf_res_base)

    log.replace("Group 1",float("nan"))

    #if roles are present in the graph, will then by default check conformance for correct assignment of roles to activities
    #dropped a role, cause deviation
    conf_res_roles = pm4py.conformance_dcr(log, graph_base, return_diagnostics_dataframe=True)
    print("both runs")
    print(conf_res_roles)

def execute_dcr_alignment():
    """
    run of the alignment of dcr graphs

    """
    log = pm4py.read_xes(os.path.join("..","tests","input_data","running-example.xes"))

    #discover base dcr graph, does not support dcr graphs with roles
    graph, _ = pm4py.discover_dcr(log)

    align_res = pm4py.optimal_alignment_dcr(log, graph,return_diagnostics_dataframe=True)
    print(align_res)

    #work with the visualization
    align_res = pm4py.optimal_alignment_dcr(log, graph)

    #works with view_alignments()
    pm4py.view_alignments(log, align_res, format='svg')

def execute_import_export():
    """
    import and export of dcr graphs
    """
    from pm4py.objects.dcr.exporter.exporter import Variants
    log = pm4py.read_xes(os.path.join("..","tests","input_data","running-example.xes"))
    graph, _ = pm4py.discover_dcr(log)

    #currently only support the base dcr graph
    pm4py.write_dcr_xml(graph,path=os.path.join("..","tests","test_output_data","dcr.xml"),
                        variant=Variants.XML_DCR_PORTAL, dcr_title="dcr graph of running-example")

    graph = pm4py.read_dcr_xml(file_path=os.path.join("..","tests","test_output_data","dcr.xml"))
    print(graph)


if __name__ == "__main__":
    execute_discover()
    execute_discover_roles()
    execute_dcr_alignment()
    execute_dcr_conformance()
    execute_import_export()
