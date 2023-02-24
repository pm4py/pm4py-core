import pm4py
import pandas as pd
import os


def execute_script():
    dataframe = pd.read_csv(os.path.join("..", "tests", "input_data", "receipt.csv"))
    dataframe = pm4py.format_dataframe(dataframe)

    # define a K-Means with 3 clusters
    from sklearn.cluster import KMeans
    clusterer = KMeans(n_clusters=3, random_state=0, n_init="auto")

    for clust_df in pm4py.cluster_log(dataframe, sklearn_clusterer=clusterer):
        print(clust_df)
        process_tree = pm4py.discover_process_tree_inductive(clust_df)
        pm4py.view_process_tree(process_tree, format="svg")


if __name__ == "__main__":
    execute_script()
