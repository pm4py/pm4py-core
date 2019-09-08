import networkx as nx
from networkx.algorithms.community.asyn_fluid import asyn_fluidc
import numpy as np

NC = "nc"
P1 = "p1"
P2 = "p2"
DEFAULT_NC = 4
DEFAULT_P1 = 0.5
DEFAULT_P2 = 0.5

def apply(frequents_label, frequents_encodings, parameters=None):
    """
    Apply a clustering algorithm (modularity maximization) on the encodings

    Parameters
    ---------------
    frequents_label
        Label of the sequences
    frequents_encodings
        Encodings of the sequences
    parameters
        Parameters of the algorithm:
            nc => numbers of clusters
            p1 => weight of the first term
            p2 => weight of the second term

    Returns
    ----------------
    communities
        Communities
    """
    if parameters is None:
        parameters = {}

    nc = parameters[NC] if NC in parameters else DEFAULT_NC

    p1 = parameters[P1] if P1 in parameters else DEFAULT_P1
    p2 = parameters[P2] if P2 in parameters else DEFAULT_P2

    G = nx.Graph()

    for i in range(len(frequents_encodings)):
        G.add_node(i)

    for i in range(len(frequents_encodings)):
        for j in range(i+1, len(frequents_encodings)):
            sim1 = np.linalg.norm(frequents_encodings[i] - frequents_encodings[j])
            as1 = set(frequents_label[i].split())
            as2 = set(frequents_label[j].split())
            sim2 = len(as1.intersection(as2))/len(as1.union(as2))
            G.add_edge(i, j, weight=p1*sim1 + p2*sim2)

    communities = list(asyn_fluidc(G, nc))

    return communities
