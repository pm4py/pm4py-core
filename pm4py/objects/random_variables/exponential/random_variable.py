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

import numpy as np

from pm4py.objects.random_variables.basic_structure import BasicStructureRandomVariable


class Exponential(BasicStructureRandomVariable):
    """
    Describes a normal variable
    """

    def __init__(self, loc=1, scale=1):
        """
        Constructor

        Parameters
        -----------
        loc
            Loc of the distribution (see docs.scipy.org/doc/scipy/reference/generated/scipy.stats.expon.html)
        scale
            Scale of the distribution
        """
        self.loc = loc
        self.scale = scale
        self.priority = 0
        BasicStructureRandomVariable.__init__(self)

    def read_from_string(self, distribution_parameters):
        """
        Initialize distribution parameters from string

        Parameters
        -----------
        distribution_parameters
            Current distribution parameters as exported on the Petri net
        """
        self.loc = 0
        self.scale = 1.0 / float(distribution_parameters)

    def get_distribution_type(self):
        """
        Get current distribution type

        Returns
        -----------
        distribution_type
            String representing the distribution type
        """
        return "EXPONENTIAL"

    def get_distribution_parameters(self):
        """
        Get a string representing distribution parameters

        Returns
        -----------
        distribution_parameters
            String representing distribution parameters
        """
        if self.scale > 0:
            return str(1.0 / float(self.scale))
        return "UNDEFINED"

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
        from scipy.stats import expon

        if len(values) > 1:
            somma = 0
            for value in values:
                somma = somma + np.log(expon.pdf(value, self.loc, self.scale))
            return somma
        return -sys.float_info.max

    def calculate_parameters(self, values):
        """
        Calculate parameters of the current distribution

        Parameters
        -----------
        values
            Empirical values to work on
        """
        from scipy.stats import expon

        if len(values) > 1:
            self.loc, self.scale = expon.fit(values, floc=0)

    def get_value(self):
        """
        Get a random value following the distribution

        Returns
        -----------
        value
            Value obtained following the distribution
        """
        from scipy.stats import expon

        return expon.rvs(self.loc, self.scale)
