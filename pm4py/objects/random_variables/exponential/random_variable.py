from scipy.stats import expon
import numpy as np
import sys


class Exponential(object):
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

    def read_from_string(self, distribution_parameters):
        """
        Initialize distribution parameters from string

        Parameters
        -----------
        distribution_parameters
            Current distribution parameters as exported on the Petri net
        """
        self.loc = distribution_parameters.split(";")[0]
        self.scale = distribution_parameters.split(";")[0]

    def get_transition_type(self):
        """
        Get the type of transition associated to the current distribution

        Returns
        -----------
        transition_type
            String representing the type of the transition
        """
        return "TIMED"

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
        return str(self.loc) + ";" + str(self.scale)

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
            sum = 0
            for value in values:
                sum = sum + np.log(expon.pdf(value, self.loc, self.scale))
            return sum
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
            self.loc, self.scale = expon.fit(values)

    def get_value(self):
        """
        Get a random value following the distribution

        Returns
        -----------
        value
            Value obtained following the distribution
        """
        return expon.rvs(self.loc, self.scale)

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

    def __str__(self):
        """
        Returns a representation of the current object

        Returns
        ----------
        repr
            Representation of the current object
        """
        return self.get_distribution_type() + " " + self.get_distribution_parameters()

    def __repr__(self):
        """
        Returns a representation of the current object

        Returns
        ----------
        repr
            Representation of the current object
        """
        return self.get_distribution_type() + " " + self.get_distribution_parameters()