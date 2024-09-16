import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# Step 1: Create a directed graph with random weights
def create_random_directed_graph(n_vertices=10):
    G = nx.DiGraph()
    G.add_nodes_from(range(n_vertices))

    # Assign random weights to directed edges (representing preferences)
    for i in range(n_vertices):
        for j in range(n_vertices):
            if i != j:
                weight = np.random.randint(1, 11)  # Random weight between 1 and 10
                G.add_edge(i, j, weight=weight)
    
    return G

# Step 2: SDP-inspired vector assignment (randomized vectors on the unit sphere)
def assign_random_vectors(n_vertices, dim=3):
    # Random vectors on the unit sphere
    vectors = np.random.randn(n_vertices, dim)
    vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors

# Step 3: Sequential assignment respecting the ranking constraint
def assign_clusters_with_ordering(vectors, n_clusters=3):
    n_vertices = vectors.shape[0]
    
    # Assume the vertices are ranked in ascending order based on their index
    ranked_vertices = np.argsort(np.arange(n_vertices))  # Vertex 0 is ranked highest, 1 is second highest, etc.
    
    # Assign the highest-ranked vertices to higher clusters
    clusters = np.zeros(n_vertices, dtype=int)
    
    # Calculate how many vertices per cluster to evenly distribute the vertices
    cluster_sizes = np.full(n_clusters, n_vertices // n_clusters)  # Base size for each cluster
    cluster_sizes[:n_vertices % n_clusters] += 1  # Distribute the remainder
    
    cluster_start = 0
    for cluster_id in range(n_clusters):
        cluster_end = cluster_start + cluster_sizes[cluster_id]
        # Assign vertices in this range to the current cluster
        clusters[ranked_vertices[cluster_start:cluster_end]] = cluster_id
        cluster_start = cluster_end
    
    return clusters

# Step 4: Visualize the graph with cluster colors
def visualize_graph(G, clusters):
    pos = nx.spring_layout(G)  # Spring layout for visualizing the graph
    colors = ['r', 'g', 'b']  # Use 3 colors for 3 clusters
    node_colors = [colors[clusters[node]] for node in G.nodes]

    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=700, font_color='white', font_weight='bold')
    
    # Draw edge labels (weights)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    
    plt.title('Graph Visualization with Clusters (Ordering Respected)')
    plt.show()

# Step 5: Main function to generate the graph, perform clustering, and visualize
def main():
    np.random.seed(42)  # Set seed for reproducibility
    
    # Create a graph with 10 vertices
    G = create_random_directed_graph(n_vertices=10)
    
    # Assign random vectors (simulating the SDP relaxation)
    vectors = assign_random_vectors(n_vertices=10)
    
    # Perform ordered assignment to 3 clusters, respecting the ranking constraint
    clusters = assign_clusters_with_ordering(vectors, n_clusters=3)
    
    # Visualize the resulting graph and clusters
    visualize_graph(G, clusters)

if __name__ == "__main__":
    main()
