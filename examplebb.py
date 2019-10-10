if __name__ == "__main__":
    import pm4pycvxopt
    from pm4py.objects.log.importer.xes import factory as xes_importer
    from pm4py.algo.discovery.inductive import factory as inductive_miner
    from pm4py.algo.conformance.alignments import factory as alignments_factory

    log = xes_importer.apply("tests/input_data/running-example.xes")
    net, im, fm = inductive_miner.apply(log)
    aligned_traces = alignments_factory.apply(log, net, im, fm)

    print(aligned_traces)

