from scipy.stats import uniform
import numpy as np


class Uniform(object):
    """
    Describes an uniform variable
    """
    def __init__(self, loc=0, scale=1):
        """
        Constructor

        Parameters
        -----------
        loc
            Start of the interval
        scale
            Scale of the interval
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

    def get_distribution_type(self):
        """
        Get current distribution type

        Returns
        -----------
        distribution_type
            String representing the distribution type
        """
        return "UNIFORM"

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
        sum = 0
        for value in values:
            sum = sum + np.log(uniform.pdf(value,self.loc,self.scale))
        return sum

    def calculate_parameters(self, values):
        """
        Calculate parameters of the current distribution

        Parameters
        -----------
        values
            Empirical values to work on
        """
        self.loc, self.scale = uniform.fit(values)

    def get_value(self):
        """
        Get a random value following the distribution

        Returns
        -----------
        value
            Value obtained following the distribution
        """
        return uniform.rvs(self.loc, self.scale)

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