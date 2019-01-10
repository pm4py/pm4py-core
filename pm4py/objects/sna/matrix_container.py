class MatrixContainer(object):
    def __init__(self, dataframe, resources_set, activities_set=None):
        if activities_set is None:
            activities_set = set()
        self.dataframe = dataframe
        self.resources_set = resources_set
        self.activities_set = activities_set

