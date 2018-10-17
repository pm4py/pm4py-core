def replace_values(dfg1, dfg2):
    """
    Replace edge values specified in a DFG by values from a (potentially bigger) DFG

    Parameters
    -----------
    dfg1
        First specified DFG (where values of edges should be replaces)
    dfg2
        Second specified DFG (from which values should be taken)

    Returns
    -----------
    dfg1
        First specified DFG with overrided values
    """
    for edge in dfg1:
        if edge in dfg2:
            dfg1[edge] = dfg2[edge]
    return dfg1
