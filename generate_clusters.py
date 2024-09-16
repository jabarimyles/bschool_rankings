import itertools

def generate_clusters_with_itertools(n, k):
    """
    Generates all possible ways to partition the numbers 1 to n into k non-empty sequential clusters.

    Parameters:
    n (int): The range of numbers (1 to n).
    k (int): The number of clusters.

    Returns:
    List of lists: Each list contains k clusters, where each cluster is a list of sequential numbers.
    """
    # Generate all combinations of k-1 partition points from the range (1, n-1)
    partition_points = itertools.combinations(range(1, n), k-1)
    
    clusters = []
    
    # For each set of partition points, generate the clusters
    for points in partition_points:
        points = (0,) + points + (n,)  # Add 0 at the start and n at the end
        current_clusters = [list(range(points[i] + 1, points[i+1] + 1)) for i in range(len(points) - 1)]
        clusters.append(current_clusters)
    
    return clusters

# Example usage:
n = 15  # Numbers 1 to 15
k = 4   # 4 clusters
clusters = generate_clusters_with_itertools(n, k)

# Print all the clusters
for i, cluster_set in enumerate(clusters, 1):
    print(f"Cluster Set {i}: {cluster_set}")
