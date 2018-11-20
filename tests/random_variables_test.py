import unittest

from pm4py.objects.random_variables.normal.random_variable import Normal
from pm4py.objects.random_variables.random_variable import RandomVariable
from pm4py.objects.random_variables.uniform.random_variable import Uniform
from pm4py.objects.random_variables.exponential.random_variable import Exponential
from pm4py.objects.random_variables.constant0.random_variable import Constant0
import os
from pm4py.objects.log.importer.xes import factory as xes_importer
from tests.constants import INPUT_DATA_DIR
from pm4py.algo.discovery.alpha import factory as alpha_miner
from pm4py.objects.stochastic_petri import map as stochastic_map
from pm4py.objects.petri.reachability_graph import construct_reachability_graph
from pm4py.visualization.transition_system import factory as ts_vis_factory
from pm4py.objects.stochastic_petri import tangible_reachability
from pm4py.objects.stochastic_petri import ctmc


class RandomVariableTest(unittest.TestCase):
    def test_uniform_variable(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        loc = 53
        scale = 32
        tol = 0.15
        U = Uniform(loc=loc, scale=scale)
        values = U.get_values(no_values=400)
        R = RandomVariable()
        R.calculate_parameters(values)
        if not R.get_distribution_type() == "UNIFORM":
            raise Exception("Expected an uniform!")
        loc_R = R.random_variable.loc
        scale_R = R.random_variable.scale
        diff_value_loc = abs(loc - loc_R) / (max(abs(loc), abs(loc_R)))
        diff_value_scale = abs(scale - scale_R) / (max(abs(scale), abs(scale_R)))
        if diff_value_loc > tol or diff_value_scale > tol:
            raise Exception("parameters found outside tolerance")

    def test_normal_variable(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        mu = 53
        sigma = 4
        tol = 0.15
        N = Normal(mu=mu, sigma=sigma)
        values = N.get_values(no_values=400)
        R = RandomVariable()
        R.calculate_parameters(values)
        if not R.get_distribution_type() == "NORMAL":
            raise Exception("Excepted a normal!")
        mu_R = R.random_variable.mu
        sigma_R = R.random_variable.sigma
        diff_value_mu = abs(mu - mu_R) / (max(abs(mu), abs(mu_R)))
        diff_value_sigma = abs(sigma - sigma_R) / (max(abs(sigma), abs(sigma_R)))
        if diff_value_mu > tol or diff_value_sigma > tol:
            raise Exception("parameters found outside tolerance")

    def test_exponential_variable(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        loc = 0
        scale = 5
        tol = 0.2
        E = Exponential(loc=loc, scale=scale)
        values = E.get_values(no_values=400)
        R = RandomVariable()
        R.calculate_parameters(values)
        if not R.get_distribution_type() == "EXPONENTIAL":
            raise Exception("Expected an exponential!")
        loc_R = R.random_variable.loc
        scale_R = R.random_variable.scale
        diff_value_loc = abs(loc - loc_R) / (max(abs(loc), abs(loc_R)) + 0.000001)
        diff_value_scale = abs(scale - scale_R) / (max(abs(scale), abs(scale_R)) + 0.000001)
        if diff_value_loc > tol or diff_value_scale > tol:
            raise Exception("parameters found outside tolerance")

    def test_constant0_variable(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        C = Constant0()
        values = []
        loglikeli = C.calculate_loglikelihood(values)
        if abs(loglikeli) < 10000000:
            raise Exception("problem in managing constant variables")
        R = RandomVariable()
        R.calculate_parameters(values)
        if not R.get_distribution_type() == "IMMEDIATE":
            raise Exception("Expected a constant!")
        loglikeli = R.calculate_loglikelihood(values)
        if abs(loglikeli) < 10000000:
            raise Exception("problem in managing constant variables (2)")

    def test_constant0_variable_2(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        C = Constant0()
        values = [0.0000001,-0.0000001,0.0000002]
        loglikeli = C.calculate_loglikelihood(values)
        if abs(loglikeli) < 10000000:
            raise Exception("problem in managing constant variables")
        R = RandomVariable()
        R.calculate_parameters(values)
        if not R.get_distribution_type() == "IMMEDIATE":
            raise Exception("Expected a constant!")
        loglikeli = R.calculate_loglikelihood(values)
        if abs(loglikeli) < 10000000:
            raise Exception("problem in managing constant variables (2)")

    def test_tangiblereachabilitygraph_calc(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.import_log(input_log)
        net, initial_marking, final_marking = alpha_miner.apply(log)
        s_map = stochastic_map.get_map_from_log_and_net(log, net, initial_marking, final_marking)
        reachab_graph = construct_reachability_graph(net, initial_marking)
        tang_reach_graph = tangible_reachability.get_tangible_reachability_from_reachability(reachab_graph,
                                                                                             s_map)
        viz = ts_vis_factory.apply(tang_reach_graph, parameters={"format": "svg", "show_labels": True})
        # gets the Q matrix assuming exponential distributions
        Q_matrix = ctmc.get_Q_matrix_from_tangible_exponential(tang_reach_graph, s_map)
        # pick a state to start from
        states = sorted(list(tang_reach_graph.states), key=lambda x: x.name)
        state = states[0]
        transient_result = ctmc.transient_analysis_from_tangible_q_matrix_and_single_state(tang_reach_graph, Q_matrix,
                                                                                           state, 86400)
        transient_result = ctmc.transient_analysis_from_tangible_q_matrix_and_single_state(tang_reach_graph, Q_matrix,
                                                                                           state, 864000)
        steady_state = ctmc.steadystate_analysis_from_tangible_q_matrix(tang_reach_graph, Q_matrix)