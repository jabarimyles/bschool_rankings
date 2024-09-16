import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from itertools import permutations, combinations

# Create a random directed graph with weights
def create_random_weighted_graph(n_vertices):
    G = nx.DiGraph()
    for i in range(n_vertices):
        for j in range(n_vertices):
            if i != j:
                G.add_edge(i, j, weight=np.random.randint(1, 10))
    return G

# Cut imbalance (CIbase) between two clusters
def cut_imbalance(G, cluster1, cluster2):
    w_XY = sum(G[i][j]['weight'] for i in cluster1 for j in cluster2 if G.has_edge(i, j))
    w_YX = sum(G[i][j]['weight'] for i in cluster2 for j in cluster1 if G.has_edge(i, j))
    
    if w_XY + w_YX == 0:
        return 0  # Avoid division by zero when no edges exist between clusters
    
    return 0.5 * abs(w_XY - w_YX) / (w_XY + w_YX)

# Calculate total cut imbalance across all cluster pairs
def total_cut_imbalance(G, clusters):
    total_CI = 0
    cluster_list = list(clusters.values())
    for i in range(len(cluster_list)):
        for j in range(i + 1, len(cluster_list)):
            total_CI += cut_imbalance(G, cluster_list[i], cluster_list[j])
    return total_CI

# Exhaustive Enumeration for Clustering, respecting vertex ordering
def enumerate_solutions(G, n_vertices, n_clusters):
    best_CI = -np.inf
    best_partition = None

    # Generate all possible ways to partition n_vertices into n_clusters (enumerate all solutions)
    partitions = combinations(permutations(range(n_vertices), n_vertices), n_clusters)

    for partition in partitions:
        clusters = {i: [] for i in range(n_clusters)}
        for i, vertices in enumerate(partition):
            clusters[i] = list(vertices)
        
        # Ensure the ordering constraint: vertices must be in increasing order within clusters
        valid_partition = True
        for cluster in clusters.values():
            if sorted(cluster) != cluster:  # Check if the cluster is sorted in increasing order
                valid_partition = False
                break
        
        if not valid_partition:
            continue  # Skip invalid partitions
        
        # Calculate total CIbase for this partition
        CI = total_cut_imbalance(G, clusters)
        
        if CI > best_CI:
            best_CI = CI
            best_partition = clusters

    return best_partition, best_CI

# Visualize the clusters, showing vertex numbers on nodes
def visualize_clusters(clusters, G):
    pos = nx.spring_layout(G)
    colors = ['r', 'g', 'b', 'y']

    for cluster_idx, members in clusters.items():
        nx.draw_networkx_nodes(G, pos, nodelist=members, node_color=colors[cluster_idx % len(colors)], label=f'Cluster {cluster_idx}')
    
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_labels(G, pos)  # Show vertex numbers on nodes
    plt.legend()
    plt.show()

# Main Execution
if __name__ == "__main__":
    # Create a random directed graph with 15 vertices
    n_vertices = 15
    n_clusters = 4
    G = create_random_weighted_graph(n_vertices)

    # Run exhaustive enumeration
    best_partition, best_CI = enumerate_solutions(G, n_vertices, n_clusters)

    print("Best partition:", best_partition)
    print("Best total cut imbalance:", best_CI)

    # Visualize the resulting clusters
    visualize_clusters(best_partition, G)
