import gurobipy as gp
from gurobipy import GRB
import numpy as np

# Define the parameters (example data; replace with real inputs)
V = ["V1", "V2", "V3", "V4", "V5"]  # Set of vertices
K = 3  # Number of clusters

weights = np.array([
    [0, 3, 1, 8, 7],
    [2, 0, 9, 4, 2],
    [8, 1, 0, 5, 2],
    [3, 3, 2, 0, 3],
    [1, 3, 1, 6, 7],
])

def convert_matrix_to_dict(weights):
    """
    Converts a square weight matrix into a dictionary of edge weights.

    Parameters:
    weights (np.ndarray): A square matrix where element (i, j) represents the weight of the arc from node i to node j.

    Returns:
    dict: A dictionary with keys as tuples representing edges (e.g., ("v1", "v2")) and values as the corresponding weights.
    """
    num_nodes = weights.shape[0]
    weight_dict = {}

    for i in range(num_nodes):
        for j in range(num_nodes):
            if weights[i, j] != 0:  # Only include edges with non-zero weight
                edge = (f"V{i+1}", f"V{j+1}")
                weight_dict[edge] = weights[i, j]

    return weight_dict
weights = convert_matrix_to_dict(weights)
#weights = {("A", "B"): 3, ("B", "C"): 5, ("A", "C"): 2}  # Edge weights
M = 1000  # Big M for linearization

# Create the model
model = gp.Model("Binary_Program")

# Decision variables
x = model.addVars(V, range(1, K+1), vtype=GRB.BINARY, name="x")  # Binary assignment to clusters
z = model.addVars([(i, j, k, l) for (i, j) in weights.keys() for k in range(1, K+1) for l in range(1, K+1)], vtype=GRB.BINARY, name="z")  # Binary product variables
g = model.addVars([(i, j, k, l) for (i, j) in weights.keys() for k in range(1, K+1) for l in range(1, K+1)], lb=0, vtype=GRB.CONTINUOUS, name="g")  # Auxiliary variables
f = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="f")  # Objective variable
p = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="p")  # Absolute value numerator

# Objective function: maximize f
model.setObjective(f, GRB.MAXIMIZE)

# Constraint (13): Reformulated constraint for f
model.addConstr(
    gp.quicksum(weights[(i, j)] * g[i, j, k, l] for (i, j) in weights for k in range(1, K+1) for l in range(1, K+1)) == p,
    "g_constraint"
)

# Linearization constraints for g = f * z
for (i, j) in weights.keys():
    for k in range(1, K+1):
        for l in range(1, K+1):
            #model.addConstr(g[i, j, k, l] <= f, f"g_ub1_{i}_{j}_{k}_{l}")
            model.addConstr(g[i, j, k, l] <= M * z[i, j, k, l], f"g_ub2_{i}_{j}_{k}_{l}")
            model.addConstr(g[i, j, k, l] >= f - M * (1 - z[i, j, k, l]), f"g_lb_{i}_{j}_{k}_{l}")
            model.addConstr(g[i, j, k, l] >= 0, f"g_nonneg_{i}_{j}_{k}_{l}")

# Assignment constraint (18)
for v in V:
    model.addConstr(gp.quicksum(x[v, k] for k in range(1, K+1)) == 1, f"assignment_{v}")


# At least one node in each cluster
for k in range(1, K+1):
    model.addConstr(gp.quicksum(x[v, k] for v in V) >= 1, f"cluster_min_{k}")

#Ranking constraints (25)
for i in range(len(V)):
    for j in range(i+1, len(V)):
        vi, vj = V[i], V[j]
        model.addConstr(
            gp.quicksum(k * x[vi, k] for k in range(1, K+1)) <= gp.quicksum(k * x[vj, k] for k in range(1, K+1)),
            f"ranking_{vi}_{vj}"
        )

# z constraints (22), (23), (24)
for (i, j) in weights.keys():
    for k in range(1, K+1):
        for l in range(1, K+1):
            model.addConstr(z[i, j, k, l] <= x[i, k], f"z_ub1_{i}_{j}_{k}_{l}")
            model.addConstr(z[i, j, k, l] <= x[j, l], f"z_ub2_{i}_{j}_{k}_{l}")
            model.addConstr(z[i, j, k, l] >= x[i, k] + x[j, l] - 1, f"z_lb_{i}_{j}_{k}_{l}")

# Additional constraints (19) and (20) for absolute values
X = gp.quicksum(weights[(i, j)] * z[i, j, k, l] for (i, j) in weights for k in range(1, K+1) for l in range(1, K+1))
Y = gp.quicksum(weights[(j, i)] * z[i, j, k, l] for (i, j) in weights for k in range(1, K+1) for l in range(1, K+1))  # Modify Y if needed
model.addConstr(p >= X - Y, "abs_val_pos")
model.addConstr(p >= Y - X, "abs_val_neg")
model.addConstr(p >= 0, "abs_val_nonneg")

# Solve the model
model.display()
model.write("model.lp")  # Saves the model in LP format
model.optimize()


def calculate_cut_imbalance(weights, x, V, K):
    """
    Calculate and print the total cut imbalance for the solution.

    Parameters:
    weights (dict): A dictionary of edge weights.
    x (gurobipy.Var): Gurobi binary variable indicating node-cluster assignments.
    V (list): List of vertices.
    K (int): Number of clusters.
    """
    # Initialize dictionaries to store weights between clusters
    w_kl = { (k, l): 0 for k in range(1, K+1) for l in range(1, K+1) }

    # Calculate weights between clusters
    for (i, j), w in weights.items():
        for k in range(1, K+1):
            for l in range(1, K+1):
                if x[i, k].x > 0.5 and x[j, l].x > 0.5:  # If nodes are in clusters k and l
                    w_kl[(k, l)] += w

    # Calculate the total cut imbalance
    total_cut_imbalance = 0
    for k in range(1, K+1):
        for l in range(k+1, K+1):  # Avoid double counting
            w_kl_value = w_kl[(k, l)]
            w_lk_value = w_kl[(l, k)]
            total_weight = w_kl_value + w_lk_value
            if total_weight > 0:
                cut_imbalance = abs(w_kl_value - w_lk_value) / total_weight
                total_cut_imbalance += cut_imbalance

    print(f"\nTotal Cut Imbalance: {total_cut_imbalance:.4f}")
    return total_cut_imbalance




# Output the results
if model.status == GRB.OPTIMAL:
    print(f"Optimal f: {f.x}")
    for v in V:
        for k in range(1, K+1):
            if x[v, k].x > 0.5:
                print(f"Vertex {v} assigned to cluster {k}")
    for v in model.getVars():
        print(f"{v.varName}: {v.x}")
    
    #model.display()

    # Calculate and print the cut imbalance
    calculate_cut_imbalance(weights, x, V, K)
