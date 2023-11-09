import pm4py
import os


def execute_script():
    dataframe = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"), return_legacy_log_object=True)

    # define a K-Means with 3 clusters
    from sklearn.cluster import KMeans
    clusterer = KMeans(n_clusters=3, random_state=0, n_init="auto")

    for clust_log in pm4py.cluster_log(dataframe, sklearn_clusterer=clusterer):
        print(clust_log)
        process_tree = pm4py.discover_process_tree_inductive(clust_log)
        pm4py.view_process_tree(process_tree, format="svg")


if __name__ == "__main__":
    execute_script()
