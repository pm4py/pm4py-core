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
class BasicStructureRandomVariable(object):
    def __init__(self):
        """
        Constructor
        """
        self.priority = 0
        self.weight = 0

    def get_weight(self):
        """
        Getter of weight

        Returns
        ----------
        weight
            Weight of the transition
        """
        return self.weight

    def set_weight(self, weight):
        """
        Setter of weight variable

        Parameters
        -----------
        weight
            Weight of the transition
        """
        self.weight = weight

    def get_priority(self):
        """
        Getter of the priority

        Returns
        -----------
        priority
            Priority of the transition
        """
        return self.priority

    def set_priority(self, priority):
        """
        Setter of the priority variable

        Parameters
        ------------
        priority
            Priority of the transition
        """
        self.priority = priority

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
        return "NORMAL"

    def get_distribution_parameters(self):
        """
        Get a string representing distribution parameters

        Returns
        -----------
        distribution_parameters
            String representing distribution parameters
        """
        return "UNDEFINED"

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

    def get_value(self):
        """
        Get a random value following the distribution

        Returns
        -----------
        value
            Value obtained following the distribution
        """
        return None

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
