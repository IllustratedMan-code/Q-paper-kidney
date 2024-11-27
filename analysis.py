import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import numpy as np
import kneed
import matplotlib.cm as cm
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D
from tqdm.rich import tqdm
import warnings
from tqdm import TqdmExperimentalWarning

warnings.filterwarnings("ignore", category=TqdmExperimentalWarning)


class GCT:
    def __init__(self, dataset_name, dataset_path):
        self.dataset_name = dataset_name
        path = dataset_path
        self.path = path
        with open(path, "r") as f:
            version_line = f.readline()
            info_line = f.readline()

        data_rows, data_columns, meta_columns, meta_rows = [
            int(i) for i in info_line.split()
        ]
        self._metadata = pd.read_csv(path, skiprows=2, nrows=meta_rows, sep="\t")
        self._data = pd.read_csv(
            path,
            skiprows=2 + meta_rows + 1,
            nrows=data_rows,
            sep="\t",
            names=self.metadata.columns,
            low_memory=False,
        )
        index_columns = self.metadata.columns.to_list()[: meta_columns + 1]
        self._metadata.set_index(index_columns, inplace=True)
        self._data.set_index(index_columns, inplace=True)

    @property
    def metadata(self):
        return self._metadata

    @property
    def data(self):
        return self._data

    def top_ten_genes_by_cluster(self):
        pass

    def elbow(self, random_state=0):
        m = self.data.to_numpy()
        fig, ax = plt.subplots()
        inertias = []
        k_values = list(range(1, 11))
        for i in tqdm(k_values, desc="creating elbow plot"):
            kmeans = KMeans(n_clusters=i, random_state=random_state)
            kmeans.fit(m)
            inertias.append(kmeans.inertia_)

        ax.plot(k_values, inertias, marker="o")
        knee = kneed.KneeLocator(
            k_values, inertias, curve="convex", direction="decreasing"
        )
        elbow_k = knee.knee
        elbow_inertia = inertias[knee.knee - 1]

        # Mark and label the elbow point
        ax.plot(elbow_k, elbow_inertia, "ro")  # Red dot

        # Customize the plot
        fig.suptitle(self.dataset_name)
        ax.set_xlabel("Number of clusters")
        ax.set_ylabel("Inertia")

        return fig

    def silhouette(self, random_state=0):
        n_clusters_range = list(range(2, 7))
        fig = plt.figure()
        fig.set_size_inches(18, 10)
        subfigs = fig.subfigures(1, len(n_clusters_range))

        X = self.data.to_numpy()
        for n_clusters, subfig in tqdm(
            zip(n_clusters_range, subfigs),
            total=len(n_clusters_range),
            desc="creating silhouette plot",
        ):
            (ax1, ax2) = subfig.subplots(2, 1)
            ax1.set_xlim([-0.1, 1])
            # The (n_clusters+1)*10 is for inserting blank space between silhouette
            # plots of individual clusters, to demarcate them clearly.
            ax1.set_ylim([0, len(X) + (n_clusters + 1) * 10])

            clusterer = KMeans(n_clusters=n_clusters, random_state=0)
            cluster_labels = clusterer.fit_predict(X)

            # The silhouette_score gives the average value for all the samples.
            # This gives a perspective into the density and separation of the formed
            # clusters
            silhouette_avg = silhouette_score(X, cluster_labels)
            # print(
            #     "For n_clusters =",
            #     n_clusters,
            #     "The average silhouette_score is :",
            #     silhouette_avg,
            # )

            # Compute the silhouette scores for each sample
            sample_silhouette_values = silhouette_samples(X, cluster_labels)

            y_lower = 10
            for i in range(n_clusters):
                # Aggregate the silhouette scores for samples belonging to
                # cluster i, and sort them
                ith_cluster_silhouette_values = sample_silhouette_values[
                    cluster_labels == i
                ]

                ith_cluster_silhouette_values.sort()

                size_cluster_i = ith_cluster_silhouette_values.shape[0]
                y_upper = y_lower + size_cluster_i

                color = cm.nipy_spectral(float(i) / n_clusters)
                ax1.fill_betweenx(
                    np.arange(y_lower, y_upper),
                    0,
                    ith_cluster_silhouette_values,
                    facecolor=color,
                    edgecolor=color,
                    alpha=0.7,
                )

                # Label the silhouette plots with their cluster numbers at the middle
                ax1.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))

                # Compute the new y_lower for next plot
                y_lower = y_upper + 10  # 10 for the 0 samples

            ax1.set_title(silhouette_avg)
            ax1.set_xlabel("silhouette coefficient")
            ax1.set_ylabel("Cluster label")

            # The vertical line for average silhouette score of all the values
            ax1.axvline(x=silhouette_avg, color="red", linestyle="--")

            ax1.set_yticks([])  # Clear the yaxis labels / ticks
            ax1.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])
            pca = PCA(n_components=2)

            X = pca.fit_transform(X)
            centers = pca.transform(clusterer.cluster_centers_)
            # 2nd Plot showing the actual clusters formed
            colors = cm.nipy_spectral(cluster_labels.astype(float) / n_clusters)
            ax2.scatter(
                X[:, 0],
                X[:, 1],
                marker=".",
                s=30,
                lw=0,
                alpha=0.7,
                c=colors,
                edgecolor="k",
            )

            # Labeling the clusters
            # centers = clusterer.cluster_centers_
            # Draw white circles at cluster centers
            ax2.scatter(
                centers[:, 0],
                centers[:, 1],
                marker="o",
                c="white",
                alpha=1,
                s=200,
                edgecolor="k",
            )

            for i, c in enumerate(centers):
                ax2.scatter(c[0], c[1], marker="$%d$" % i, alpha=1, s=50, edgecolor="k")

            ax2.set_title("The visualization of the clustered data.")
            ax2.set_xlabel("PCA 1")
            ax2.set_ylabel("PCA 2")

            # fig.suptitle(
            #     f"Silhouette analysis for KMeans clustering in {self.dataset_name}",
            #     fontsize=14,
            #     fontweight="bold",
            # )
        return fig


metadata = pd.read_csv("metadata.csv")


def determine_ideal_k_clustering():
    for index, row in metadata.iterrows():
        name = row["shortname"]
        d = name.replace(" ", "-")
        path = row["path"]
        gct = GCT(name, path)
        gct.data.to_csv(f"tables/{path}", index=False)
        gct.elbow().savefig(f"figures/{d}_elbow.png")
        s = gct.metadata.loc["sample_type"].values[0]
        gct._data = gct.data[gct.data.columns[s == "Primary Solid Tumor"]]
        gct.elbow().savefig(f"figures/{d}_primary-solid-tumor_elbow.png")
        gct.silhouette().savefig(
            f"figures/{d}_primary-solid-tumor_elbow_silhouette.png"
        )


determine_ideal_k_clustering()
