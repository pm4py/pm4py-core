'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
import numpy as np

from pm4py.objects.random_variables.constant0.random_variable import Constant0
from pm4py.objects.random_variables.deterministic.random_variable import Deterministic
from pm4py.objects.random_variables.exponential.random_variable import Exponential
from pm4py.objects.random_variables.normal.random_variable import Normal
from pm4py.objects.random_variables.uniform.random_variable import Uniform
from pm4py.objects.random_variables.lognormal.random_variable import LogNormal
from pm4py.objects.random_variables.gamma.random_variable import Gamma


class RandomVariable(object):
    def __init__(self):
        self.random_variable = None

    def read_from_string(self, distribution_type, distribution_parameters):
        """
        Read the random variable from string

        Parameters
        -----------
        distribution_type
            Distribution type
        distribution_parameters
            Distribution parameters splitted by ;
        """
        if distribution_type == "NORMAL":
            self.random_variable = Normal()
            self.random_variable.read_from_string(distribution_parameters)
        elif distribution_type == "UNIFORM":
            self.random_variable = Uniform()
            self.random_variable.read_from_string(distribution_parameters)
        elif distribution_type == "EXPONENTIAL":
            self.random_variable = Exponential()
            self.random_variable.read_from_string(distribution_parameters)
        elif distribution_type == "LOGNORMAL":
            self.random_variable = LogNormal()
            self.random_variable.read_from_string(distribution_parameters)
        elif distribution_type == "GAMMA":
            self.random_variable = Gamma()
            self.random_variable.read_from_string(distribution_parameters)
        elif distribution_type == "DETERMINISTIC":
            self.random_variable = Deterministic()
            self.random_variable.read_from_string(distribution_parameters)
        elif distribution_type == "IMMEDIATE":
            self.random_variable = Constant0()

    def get_distribution_type(self):
        """
        Get current distribution type

        Returns
        -----------
        distribution_type
            String representing the distribution type
        """
        if self.random_variable is not None:
            return self.random_variable.get_distribution_type()

    def get_transition_type(self):
        """
        Get the type of transition associated to the current distribution

        Returns
        -----------
        transition_type
            String representing the type of the transition
        """
        if self.random_variable is not None:
            return self.random_variable.get_transition_type()

    def get_distribution_parameters(self):
        """
        Get a string representing distribution parameters

        Returns
        -----------
        distribution_parameters
            String representing distribution parameters
        """
        if self.random_variable is not None:
            return self.random_variable.get_distribution_parameters()

    def calculate_loglikelihood(self, values):
        """
        Calculate log likelihood

        Parameters
        ------------
        values
            Empirical values to work on

        Returns
        ------------
        likelihood
            Log likelihood that the values follows the distribution
        """
        if self.random_variable is not None:
            return self.random_variable.calculate_loglikelihood(values)

    def calculate_parameters(self, values, parameters=None, force_distribution=None):
        """
        Calculate parameters of the current distribution

        Parameters
        -----------
        values
            Empirical values to work on
        parameters
            Possible parameters of the algorithm
        force_distribution
            If provided, distribution to force usage (e.g. EXPONENTIAL)

        """

        if parameters is None:
            parameters = {}

        debug_mode = parameters["debug"] if "debug" in parameters else False

        if self.random_variable is not None:
            self.random_variable.calculate_parameters(values)
        else:
            norm = Normal()
            unif = Uniform()
            expon = Exponential()
            constant = Constant0()
            lognormal = LogNormal()
            gamma = Gamma()

            if not force_distribution or not force_distribution == "EXPONENTIAL":
                likelihoods = list()
                likelihoods.append([constant, constant.calculate_loglikelihood(values)])
                if force_distribution == "NORMAL" or force_distribution is None:
                    norm.calculate_parameters(values)
                    likelihoods.append([norm, norm.calculate_loglikelihood(values)])
                if force_distribution == "UNIFORM" or force_distribution is None:
                    unif.calculate_parameters(values)
                    likelihoods.append([unif, unif.calculate_loglikelihood(values)])
                if force_distribution == "EXPONENTIAL" or force_distribution is None:
                    expon.calculate_parameters(values)
                    likelihoods.append([expon, expon.calculate_loglikelihood(values)])
                likelihoods = [x for x in likelihoods if str(x[1]) != 'nan']
                likelihoods = sorted(likelihoods, key=lambda x: x[1], reverse=True)

                if debug_mode:
                    print("likelihoods = ", likelihoods)

                self.random_variable = likelihoods[0][0]
            else:
                avg_values = np.average(values)
                if values and avg_values > 0.00000:
                    expon.scale = avg_values
                    self.random_variable = expon
                else:
                    self.random_variable = constant

    def get_value(self):
        """
        Get a random value following the distribution

        Returns
        -----------
        value
            Value obtained following the distribution
        """
        if self.random_variable is not None:
            return self.random_variable.get_value()

    def get_values(self, no_values=400):
        """
        Get some random values following the distribution

        Parameters
        -----------
        no_values
            Number of values to return

        Returns
        ----------
        values
            Values extracted according to the probability distribution
        """
        if self.random_variable is not None:
            return self.random_variable.get_values(no_values=no_values)

    def get_weight(self):
        """
        Getter of weight

        Returns
        ----------
        weight
            Weight of the transition
        """
        if self.random_variable is not None:
            return self.random_variable.get_weight()

    def set_weight(self, weight):
        """
        Setter of the weight

        Parameters
        -----------
        weight
            Weight of the transition
        """
        if self.random_variable is not None:
            self.random_variable.set_weight(weight)

    def get_priority(self):
        """
        Getter of the priority

        Returns
        -----------
        priority
            Priority of the transition
        """
        if self.random_variable is not None:
            return self.random_variable.get_priority()

    def set_priority(self, priority):
        """
        Setter of the priority variable

        Parameters
        ------------
        priority
            Priority of the transition
        """
        if self.random_variable is not None:
            self.random_variable.set_priority(priority)

    def __str__(self):
        """
        Returns a representation of the current object

        Returns
        ----------
        repr
            Representation of the current object
        """
        if self.random_variable is not None:
            return str(self.random_variable)
        else:
            return "UNINITIALIZED"

    def __repr__(self):
        """
        Returns a representation of the current object

        Returns
        ----------
        repr
            Representation of the current object
        """
        if self.random_variable is not None:
            return repr(self.random_variable)
        else:
            return "UNINITIALIZED"
