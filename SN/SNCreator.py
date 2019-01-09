'''
Created on Oct 5, 2018

@author: majid
'''
from _collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from pyvis.network import Network
from scipy.stats import pearsonr


class SNCreator(object):

    def __init__(self, resourceList, activityList, snDataFrame):
        """
        Constructor

        Parameters
        -------------
        resourceList
            List of resources contained in the log
        activityList
            List of activities contained in the log
        snDataFrame
            Social Network dataframe (full or basic)
        """
        self.resourceList = resourceList.copy()
        self.activityList = activityList.copy()
        self.snDataFrame = snDataFrame

    def makeEmptyRscRscMatrix(self):
        """
        Make an empty numpy matrix with the rows and columns which are resource list
        """
        RscRscMatrix = np.zeros([len(self.resourceList), len(self.resourceList)])  # +1 is just for considering <None>
        return RscRscMatrix;

    def makeEmptyRscActMatrix(self):
        """
        Make an empty numpy matrix with the rows that are resources, and the columns that are activities
        """
        RscActMatrix = np.zeros([len(self.resourceList), len(self.activityList)])  # +1 is just for considering <None>
        return RscActMatrix;

    def makeHandoverMatrix(self):
        """
        Building the Handover matrix

        Returns
        ------------
        RscRscMatrix
            Resource-Resource Matrix
        """
        RscRscMatrix = SNCreator.makeEmptyRscRscMatrix(self)

        for resource, next_resource in zip(self.snDataFrame['resource'], self.snDataFrame['next_resource']):
            RscRscMatrix[self.resourceList.index(resource)][self.resourceList.index(next_resource)] += 1

        return RscRscMatrix

    def makeRealHandoverMatrix(self, dependency_threshold):
        """
        Make the Real Handover matrix

        Parameters
        -------------
        dependency_threshold
            Dependency threshold to find real causal relations
        """
        RscRscMatrix = SNCreator.makeEmptyRscRscMatrix(self)

        groupedbyactivityPairs = self.snDataFrame.groupby(['activity', 'next_activity']).size().reset_index(
            name='counts')

        for index, row in self.snDataFrame.iterrows():
            ab = groupedbyactivityPairs.loc[(groupedbyactivityPairs['activity'] == row['activity']) & (
                    groupedbyactivityPairs['next_activity'] == row['next_activity'])]
            if (ab.empty):
                abn = 0
            else:
                abn = ab.iloc[0, 2]
            ba = groupedbyactivityPairs.loc[(groupedbyactivityPairs['next_activity'] == row['activity']) & (
                    groupedbyactivityPairs['activity'] == row['next_activity'])]
            if (ba.empty):
                ban = 0
            else:
                ban = ab.iloc[0, 2]
            if (row['activity'] == row['next_activity']):
                dependency = (abn) / (abn + 1)
            else:
                dependency = (abn - ban) / (abn + ban + 1)

            if (dependency > dependency_threshold):
                RscRscMatrix[self.resourceList.index(row['resource'])][
                    self.resourceList.index(row['next_resource'])] += 1

        return RscRscMatrix

    def makeJointActivityMatrix(self):
        """
        Calculate the Joint Activities matrix

        Returns
        ------------
        RscActMatrix
            Resource-activity matrix
        """
        allresources = np.concatenate([self.snDataFrame['resource'], self.snDataFrame['next_resource']], axis=0)
        allactivities = np.concatenate([self.snDataFrame['activity'], self.snDataFrame['next_activity']], axis=0)

        all_resource_activity = np.concatenate(
            [allresources.reshape(len(allresources), 1), allactivities.reshape(len(allactivities), 1)], axis=1)
        all_resource_activity_df = pd.DataFrame(columns=['resource', 'activity'],
                                                data=all_resource_activity)

        groupedbyactivity = all_resource_activity_df.groupby(['resource'])
        resource_activity_dict = defaultdict(list)

        for resource, group in groupedbyactivity:
            resource_activity_dict[resource].append(group[
                                                        'activity'].values)  # if I use "values", for some values which are not start or end activities, we will have one more frequency (unique())

        RscActMatrix = SNCreator.makeEmptyRscActMatrix(self)

        for resource in resource_activity_dict:
            for activity_list in resource_activity_dict[resource]:
                for activity in activity_list:
                    RscActMatrix[self.resourceList.index(resource)][self.activityList.index(activity)] += 1

        return RscActMatrix

    def makeEmptyActRscMatrix(self):
        ActRscMatrix = np.zeros([len(self.activityList), len(self.resourceList)])  # +1 is just for considering <None>
        return ActRscMatrix;

    def makeActivityRscMatrix(self):
        allresources = np.concatenate([self.snDataFrame['resource'], self.snDataFrame['next_resource']], axis=0)
        allactivities = np.concatenate([self.snDataFrame['activity'], self.snDataFrame['next_activity']], axis=0)

        all_resource_activity = np.concatenate(
            [allresources.reshape(len(allresources), 1), allactivities.reshape(len(allactivities), 1)], axis=1)
        all_resource_activity_df = pd.DataFrame(columns=['resource', 'activity'],
                                                data=all_resource_activity)

        groupedbyactivity = all_resource_activity_df.groupby(['activity'])
        resource_activity_dict = defaultdict(list)

        for activity, group in groupedbyactivity:
            resource_activity_dict[activity].append(group[
                                                        'resource'].values)  # if I use "values", for some values which are not start or end activities, we will have one more frequency (unique())

        ActRscMatrix = SNCreator.makeEmptyActRscMatrix(self)

        for activity in resource_activity_dict:
            for resource_list in resource_activity_dict[activity]:
                for resource in resource_list:
                    ActRscMatrix[self.activityList.index(activity)][self.resourceList.index(resource)] += 1

        return ActRscMatrix

    def makeActivityPairs(self):
        groupedbyactivityPairs = self.snDataFrame.groupby(['activity', 'next_activity']).size().reset_index(
            name='counts')
        return groupedbyactivityPairs

    def convertRscAct2RscRsc(self, RscActMatrix, method):
        """
        Converting Resource-Activity matrix to Resource-Resource matrix based
        on the similarity measure

        Parameters
        -------------
        RscActMatrix
            Resource-Activity matrix
        method
            Method (pearson)
        """
        RscRscMatrix = SNCreator.makeEmptyRscRscMatrix(self)
        for index, resouce in enumerate(RscActMatrix):
            for rest in range(index + 1, RscActMatrix.shape[0]):
                main_resource = resouce
                other_resource = RscActMatrix[rest]
                if (method == "pearson"):
                    r, p = pearsonr(main_resource, other_resource)
                    RscRscMatrix[index][rest] = r
                """elif (method == "mine"):
                    similarity = SNCreator.my_similarity(self, main_resource, other_resource, False)
                    RscRscMatrix[index][rest] = similarity"""
        return RscRscMatrix

    def getResourceList(self):
        """
        Gets the resource list

        Returns
        -------------
        resourceList
            List of resources
        """
        return self.resourceList

    def getActivityList(self):
        """
        Gets the activity list

        Returns
        --------------
        activityList
            List of activities
        """
        return self.activityList

    def setResourceList(self, resourceList):
        """
        Sets the resource list

        Parameters
        --------------
        resourceList
            List of resources
        """
        self.resourceList = resourceList.copy()

    def setActivityList(self, activityList):
        """
        Sets the activity list

        Parameters
        -------------
        activityList
            List of activities
        """
        self.activityList = activityList.copy()

    def drawRscRscGraph_simple(self, RscRscMatrix, weight_threshold, directed):
        """
        Draw, based on NetworkX, which is not interactive

        Parameters
        -------------
        RscRscMatrix
            Resource-Resource matrix
        weight_threshold
            Weight threshold (to have a relation between two resources)
        directed
            Boolean that specifies if the graph is directed or not
        """
        rows, cols = np.where(RscRscMatrix > weight_threshold)
        edges = zip(rows.tolist(), cols.tolist())

        if (directed):
            G = nx.DiGraph()
        else:
            G = nx.Graph()

        labels = {}
        nodes = []
        for index, item in enumerate(self.resourceList):
            labels[index] = item
            nodes.append(index)

        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx.draw(G, with_labels=True, node_color=['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0'], labels=labels,
                node_size=500, pos=nx.circular_layout(G))
        plt.show()

    def drawRscRscGraph_advanced(self, RscRscMatrix, weight_threshold, directed):
        """
        Draw, based on Pyviz, an interactive web page that shows the Social Network

        Parameters
        -------------
        RscRscMatrix
            Resource-Resource matrix
        weight_threshold
            Weight threshold (to have a relation between two resources)
        directed
            Boolean that specifies if the graph is directed or not
        """
        rows, cols = np.where(RscRscMatrix > weight_threshold)
        weights = list();

        for x in range(len(rows)):
            weights.append(RscRscMatrix[rows[x]][cols[x]])

        got_net = Network(height="750px", width="100%", bgcolor="black", font_color="#3de975", directed=directed)
        ##f57b2b
        # set the physics layout of the network
        got_net.barnes_hut()

        edge_data = zip(rows, cols, weights)

        for e in edge_data:
            src = self.resourceList[e[0]]  # convert ids to labels
            dst = self.resourceList[e[1]]
            w = e[2]

            # I have to add some options here, there is no parameter
            highlight = {'border': "#3de975", 'background': "#41e9df"}
            # color = {'border': "#000000", 'background': "#123456"}
            got_net.add_node(src, src, title=src, labelHighlightBold=True, color={'highlight': highlight})
            got_net.add_node(dst, dst, title=dst, labelHighlightBold=True, color={'highlight': highlight})
            got_net.add_edge(src, dst, value=w, title=w)

        neighbor_map = got_net.get_adj_list()

        dict = got_net.get_edges()

        self.getResourceList()

        # add neighbor data to node hover data
        for node in got_net.nodes:
            counter = 0
            if (directed):
                node["title"] = "<h3>" + node["title"] + " Output Links: </h3>"
            else:
                node["title"] = "<h3>" + node["title"] + " Links: </h3>"
            for neighbor in neighbor_map[node["id"]]:
                if (counter % 10 == 0):
                    node["title"] += "<br>::: " + neighbor
                else:
                    node["title"] += " ::: " + neighbor
                node["value"] = len(neighbor_map[node["id"]])
                counter += 1

        got_net.show_buttons(filter_=['nodes', 'edges', 'physics'])

        got_net.show("PMSocial.html")
