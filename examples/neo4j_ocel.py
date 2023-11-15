import pm4py
from neo4j import GraphDatabase
from examples import examples_conf
from pm4py.util import nx_utils


def execute_script():
    ocel = pm4py.read_ocel2("../tests/input_data/ocel/ocel20_example.jsonocel")
    #ocel = pm4py.read_ocel("../tests/input_data/ocel/ocel_order_simulated.csv")

    # prints the actual contents of the OCEL
    print(ocel)

    uri = "neo4j://localhost:7687"
    username = "neo4j"
    password = "ciaociao"

    driver = GraphDatabase.driver(uri, auth=(username, password))

    with driver.session() as session:
        # transforms the OCEL to a NetworkX DiGraph
        nx_graph = pm4py.convert_ocel_to_networkx(ocel)

        # uploads the NetworkX DiGraph (representing the OCEL) to Neo4J
        nx_utils.neo4j_upload(nx_graph, session)

        # gets back the same NetworkX DiGraph starting from Neo4J
        nx_graph2 = nx_utils.neo4j_download(session)

        # convert the obtained NetworkX DiGraph into an OCEL
        ocel2 = nx_utils.nx_to_ocel(nx_graph2)

        # prints the contents of the 'new' OCEL
        print(ocel2)

        # shows the object-centric directly-follows graph on the screen
        ocdfg = pm4py.discover_ocdfg(ocel2)
        pm4py.view_ocdfg(ocdfg, annotation="frequency", format=examples_conf.TARGET_IMG_FORMAT)
        pm4py.view_ocdfg(ocdfg, annotation="performance", format=examples_conf.TARGET_IMG_FORMAT)


if __name__ == "__main__":
    execute_script()
