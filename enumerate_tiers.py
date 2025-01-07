import itertools
import numpy as np

def compute_cut_imbalance(tiers, weights):
    total_cut_imbalance = 0
    num_tiers = len(tiers)
    for i in range(num_tiers):
        for j in range(num_tiers):
            if i != j:
                w_ij = sum(weights[u][v] for u in tiers[i] for v in tiers[j])
                w_ji = sum(weights[u][v] for u in tiers[j] for v in tiers[i])
                if w_ij + w_ji > 0:
                    total_cut_imbalance += abs(w_ij - w_ji) / (w_ij + w_ji)
    return total_cut_imbalance / 2

def enumerate_sequential_tier_splits(num_nodes, num_tiers, weights):
    nodes = list(range(num_nodes))
    best_split = None
    best_cut_imbalance = float('-inf')

    # Generate all possible split points for the tiers
    for split_points in itertools.combinations(range(1, num_nodes), num_tiers - 1):
        split_points = (0,) + split_points + (num_nodes,)
        tiers = [nodes[split_points[i]:split_points[i + 1]] for i in range(num_tiers)]

        cut_imbalance = compute_cut_imbalance(tiers, weights)
        print(f"Split point:  {split_points}, cut imbalance: {cut_imbalance}")
        if cut_imbalance > best_cut_imbalance:
            best_cut_imbalance = cut_imbalance
            best_split = tiers

    return best_split, best_cut_imbalance

def ensure_square_weights(weights):
    rows, cols = weights.shape
    if rows != cols:
        raise ValueError("Weight matrix must be square. Provided matrix has dimensions {}x{}.".format(rows, cols))
    return weights

if __name__ == "__main__":
    num_tiers = 3

    weights = np.array([
    [0, 3, 1, 8, 7],
    [2, 0, 9, 4, 2],
    [8, 1, 0, 5, 2],
    [3, 3, 2, 0, 3],
    [1, 3, 1, 6, 7],
    ])

    ensure_square_weights(weights)

    num_nodes = weights.shape[0]

    best_split, best_cut_imbalance = enumerate_sequential_tier_splits(num_nodes, num_tiers, weights)

    print(f"Best Tier Split: {best_split} with a cut imbalance of {best_cut_imbalance}")
