'''
Created on Oct 5, 2018

@author: majid
'''

import pandas as pd


class Utilities():
    '''
    classdocs
    '''

    def __init__(self, log):
        """
        Constructor

        Parameters
        ------------
        log
            Trace log
        """
        self.log = log
        # sets everything to empty
        self.resourceSet = set()
        self.activitySet = set()
        self.resourceList = list()
        self.activityList = list()

    def create_basic_matrix(self):
        """
        Create basic matrix (containing only resources) from the trace log object

        Returns
        ------------
        basic_df
            Basic Dataframe of Social Network
        resourceList
            List of resources contained in the log
        """
        snBasicList = [];
        for case_index, case in enumerate(self.log):
            for event_index, event in enumerate(case):
                if (len(snBasicList) > 0 and case_index == snBasicList[len(snBasicList) - 1]['trace_id']):
                    try:
                        snBasicList[len(snBasicList) - 1]['next_resource'] = event["org:resource"]
                    except KeyError:
                        snBasicList[len(snBasicList) - 1]['next_resource'] = ":None:"
                    # else:

                if (event_index == len(case) - 1):  # if it is the last event of the case, we will ignore it.
                    continue  # because we need just the resource of it which is accessed by the previous statement

                sndict = {};
                try:
                    sndict['resource'] = event["org:resource"]
                except KeyError:
                    sndict['resource'] = ":None:"

                sndict['next_resource'] = ""
                sndict['relation_depth'] = "1"
                sndict['trace_length'] = len(case)
                sndict['trace_id'] = case_index
                snBasicList.append(sndict)

        basic_df = pd.DataFrame(snBasicList)
        Utilities.setResourceSetList(self, basic_df)

        return basic_df, self.resourceList;

    def create_full_matrix(self):
        """
        Create full matrix (containing resources and activities) from the trace log object

        Returns
        ------------
        full_df
            Full dataframe of Social Network
        resourceList
            List of resources contained in the log
        activityList
            List of activities contained in the log
        """
        snFullList = [];
        for case_index, case in enumerate(self.log):
            for event_index, event in enumerate(case):
                if (len(snFullList) > 0 and case_index == snFullList[len(snFullList) - 1]['trace_id']):
                    try:
                        snFullList[len(snFullList) - 1]['next_resource'] = event["org:resource"]
                    except KeyError:
                        snFullList[len(snFullList) - 1]['next_resource'] = ":None:"
                        try:
                            snFullList[len(snFullList) - 1]['next_activity'] = event["concept:name"]
                        except KeyError:
                            snFullList[len(snFullList) - 1]['next_activity'] = ":None:"
                    else:
                        try:
                            snFullList[len(snFullList) - 1]['next_activity'] = event["concept:name"]
                        except KeyError:
                            snFullList[len(snFullList) - 1]['next_activity'] = ":None:"

                if (event_index == len(case) - 1):  # if it is the last event of the case, we will ignore it.
                    continue  # because we need just the resource of it which is accessed by the previous statement

                sndict = {};
                try:
                    sndict['resource'] = event["org:resource"]
                except KeyError:
                    sndict['resource'] = ":None:"

                sndict['next_resource'] = ""

                try:
                    sndict['activity'] = event["concept:name"]
                except KeyError:
                    sndict['activity'] = ":None:"

                sndict['next_activity'] = ""
                sndict['relation_depth'] = "1"
                sndict['trace_length'] = len(case)
                sndict['trace_id'] = case_index
                snFullList.append(sndict)

        full_df = pd.DataFrame(snFullList)
        Utilities.setResourceSetList(self, full_df)
        Utilities.setActivitySetList(self, full_df)

        return full_df, self.resourceList, self.activityList

    def setResourceSetList(self, snMatrix):
        """
        Sets the resource set list from the Social Network dataframe

        Parameters
        -------------
        snMatrix
            Social Network dataframe (basic or full matrix)
        """
        unique_resources = snMatrix['resource'].unique()
        unique_next_resources = snMatrix['next_resource'].unique()
        self.resourceSet = set(unique_resources) | set(unique_next_resources)
        self.resourceList = list(self.resourceSet)

    def setActivitySetList(self, snMatrix):
        """
        Sets the activity set list from the Social Network dataframe

        Parameters
        ------------
        snMatrix
            Social Network dataframe (only full matrix)
        """
        unique_activities = snMatrix['activity'].unique()
        unique_next_activities = snMatrix['next_activity'].unique()
        self.activitySet = set(unique_activities) | set(unique_next_activities)
        self.activityList = list(self.activitySet)
