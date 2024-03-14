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
import sys

from pm4py.objects.random_variables.basic_structure import BasicStructureRandomVariable


class Deterministic(BasicStructureRandomVariable):
    """
    Describes a deterministic random variable
    """

    def __init__(self, value=0):
        """
        Constructor

        Parameters
        ----------
        value
            Constant value of the distribution
        """
        BasicStructureRandomVariable.__init__(self)
        self.value = value
        self.priority = 1

    def read_from_string(self, distribution_parameters):
        """
        Initialize distribution parameters from string

        Parameters
        -----------
        distribution_parameters
            Current distribution parameters as exported on the Petri net
        """
        self.value = distribution_parameters

    def get_transition_type(self):
        """
        Get the type of transition associated to the current distribution

        Returns
        -----------
        transition_type
            String representing the type of the transition
        """
        return "DETERMINISTIC"

    def get_distribution_type(self):
        """
        Get current distribution type

        Returns
        -----------
        distribution_type
            String representing the distribution type
        """
        return "DETERMINISTIC"

    def get_distribution_parameters(self):
        """
        Get a string representing distribution parameters

        Returns
        -----------
        distribution_parameters
            String representing distribution parameters
        """
        return str(self.value)

    def get_value(self):
        """
        Get a random value following the distribution

        Returns
        -----------
        value
            Value obtained following the distribution
        """
        return self.value

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
        return [self.get_value() for i in range(no_values)]

    def calculate_loglikelihood(self, values, tol=0.0001):
        """
        Calculate log likelihood

        Parameters
        ------------
        values
            Empirical values to work on
        tol
            Tolerance about float values (consider them 0?)

        Returns
        ------------
        likelihood
            Log likelihood that the values follows the distribution
        """
        values_0 = [x for x in values if abs(x-self.value) < tol]
        if len(values) == len(values_0):
            return sys.float_info.max
        return -sys.float_info.max
