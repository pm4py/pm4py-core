import pm4py


def execute_script():
    # example on how stochastic Petri nets are defined, discovered and used in pm4py
    log = pm4py.read_xes("../tests/input_data/running-example.xes", return_legacy_log_object=True)

    # first, we use a traditional process discovery algorithm (the inductive miner) to discover
    # a sound workflow net from the event log
    net, im, fm = pm4py.discover_petri_net_inductive(log)

    # then, we can either define manually the distributions on the stochastic Petri net, or discover them from the log
    # in the following lines, we automatically discover the stochastic map from the log
    from pm4py.algo.simulation.montecarlo.utils import replay
    smap0 = replay.get_map_from_log_and_net(log, net, im, fm)

    # each transition of the original Petri net is associated to a stochastic variable, having a priority, a weight
    # and a stochastic distribution on the firing times.
    for trans in smap0:
        print("\n")
        print(trans)
        print(dir(smap0[trans]))
        # priority says: if in a marking a transition with higher priority
        # is enabled, it should be considered before all the other transitions
        # with lower priority disregarding the weight
        print(smap0[trans].get_priority())
        # weight sets the probability to fire the transition among all the
        # transitions with the same priority
        print(smap0[trans].get_weight())
        # sets the random variable (independently from the weight)
        print(smap0[trans].random_variable)

    # as an alternative to discover the stochastic map from the log, we can define manually the stochastic map
    # (for example, we set all the invisible to zero firing times, and the other transitions' execution times
    # is set to a normal with average 1 and standard deviation 1
    from pm4py.objects.random_variables.normal.random_variable import Normal
    from pm4py.objects.random_variables.constant0.random_variable import Constant0

    smap = {}
    for t in net.transitions:
        if t.label == "register request" or t.label is None:
            v = Constant0()
        else:
            v = Normal(mu=1, sigma=1)
        smap[t] = v

    # eventually, we can use the stochastic Petri net with a specialized algorithm,
    # such as the stochastic playout
    from pm4py.algo.simulation.playout.petri_net.variants import stochastic_playout
    ret_log = stochastic_playout.apply(net, im, fm, parameters={"smap": smap0})
    print(ret_log)


if __name__ == "__main__":
    execute_script()
