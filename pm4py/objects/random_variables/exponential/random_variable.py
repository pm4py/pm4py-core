import sys

import numpy as np
from scipy.stats import expon

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
        return expon.rvs(self.loc, self.scale)
