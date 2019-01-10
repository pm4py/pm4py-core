class MatrixContainer(object):
    def __init__(self, dataframe, resources_set, activities_set=None):
        """
        Constructor

        Parameters
        -------------
        dataframe
            Pandas dataframe
        resources_set
            Set of resources in the log
        activities_set
            Set of activities in the log
        """
        if activities_set is None:
            activities_set = set()
        self.dataframe = dataframe
        self.resources_set = resources_set
        self.activities_set = activities_set
        self.resources_list = list(resources_set)
        self.activities_list = list(activities_set)

    def contains_activities(self):
        """
        Check if this object contains the activities
        """
        return len(self.activities_list) > 0
