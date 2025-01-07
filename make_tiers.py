from ast import And
import gurobipy as gp
from gurobipy import GRB

# Parameters (Example values, you will need to replace with actual data)
V = ["v1", "v2", "v3"]  # Set of vertices (rankings)
K = 3  # Total number of clusters
weights = {('v1', 'v2'): 3, ('v2', 'v1'): 2, ('v1', 'v3'): 4, ('v3', 'v1'): 1, ('v2', 'v3'): 5, ('v3', 'v2'): 3}  # Arc weights
epsilon = 1e-6  # Small constant to avoid division by zero

# Create model
model = gp.Model("tiering_qp")

# Decision variables
x = model.addVars(V, range(K), vtype=GRB.BINARY, name="x")  # x[v, k] is 1 if vertex v is in cluster k
z = model.addVars(V, V, range(K), range(K), vtype=GRB.BINARY, name="z")  # Auxiliary variables for product linearization
f = model.addVar(lb=0, name="f")  # Objective variable
p = model.addVar(lb=0, name="p")  # Auxiliary variable for positive part
q = model.addVar(lb=0, name="q")  # Auxiliary variable for negative part

# Constraint 1: Each vertex must be assigned to exactly one cluster
model.addConstrs((gp.quicksum(x[v, k] for k in range(K)) == 1 for v in V), name="cluster_assignment")

# Constraint 2: Product linearization constraints (updated for non-equal indices)
model.addConstrs(
    (z[i, j, k, l] <= x[i, k] for i in V for j in V for k in range(K) for l in range(K) if i != j and k != l),
    name="z1"
)
model.addConstrs(
    (z[i, j, k, l] <= x[j, l] for i in V for j in V for k in range(K) for l in range(K) if i != j and k != l),
    name="z2"
)
model.addConstrs(
    (z[i, j, k, l] >= x[i, k] + x[j, l] - 1 for i in V for j in V for k in range(K) for l in range(K) if i != j and k != l),
    name="z3"
)

# Constraint 2.1: Ensure z[i, j, k, l] equals x[i, k] * x[j, l] (optional, same filtering applied)
model.addConstrs(
    (z[i, j, k, l] == x[i, k] * x[j, l] for i in V for j in V for k in range(K) for l in range(K) if i != j and k != l),
    name="z_equals_product"
)

# Define expressions for X and Y (updated for non-equal indices)
X_expr = gp.quicksum(weights[i, j] * z[i, j, k, l] for i in V for j in V for k in range(K) for l in range(K)
                     if (i, j) in weights and (i != j and k != l))
Y_expr = gp.quicksum(weights[j, i] * z[j, i, k, l] for i in V for j in V for k in range(K) for l in range(K)
                     if (j, i) in weights and (i != j and k != l))

# Constraint 3: Linearization of absolute value (applies to filtered X and Y)
model.addConstr(p - q == X_expr - Y_expr, name="abs_val_diff")
model.addConstr(p >= X_expr - Y_expr, name="abs_val_diff2")
model.addConstr(q >= Y_expr - X_expr, name="abs_val_diff3")

model.addConstr(p >= 0, name="p_nonneg")
model.addConstr(q >= 0, name="q_nonneg")

# Constraint 4: Relate f to p and q
model.addConstr(f * (X_expr + Y_expr ) == p + q, name="f_constraint")

# Constraint 5: Ordering constraint for clusters (updated for i < j)
model.addConstrs(
    (gp.quicksum(k * x[i, k] for k in range(K)) <= gp.quicksum(k * x[j, k] for k in range(K))
     for i in V for j in V if i < j),
    name="ordering_constraint"
)

# Ensure at least one node is assigned to each tier
model.addConstrs((gp.quicksum(x[v, k] for v in V) >= 1 for k in range(K)), name="min_nodes_per_tier")


# Bound auxiliary variables p and q
#MAX_PQ = sum(weights.values())  # Example: Sum of all weights as an upper bound
#model.addConstr(p <= MAX_PQ, name="bound_p")
#model.addConstr(q <= MAX_PQ, name="bound_q")




# Set the objective to maximize f
model.setObjective(f, GRB.MAXIMIZE)

# Optimize the model
model.optimize()

if model.status == GRB.INF_OR_UNBD:
    model.setParam('DualReductions', 0)  # Disable dual reductions for proper IIS computation
    model.optimize()
    if model.status == GRB.INFEASIBLE:
        print("The model is infeasible.")
        model.computeIIS()
        model.write("infeasible_model.ilp")  # Write IIS to a file for inspection
        print("IIS written to infeasible_model.ilp")
    elif model.status == GRB.UNBOUNDED:
        print("The model is unbounded.")
    else:
        print("Model is neither infeasible nor unbounded after re-optimization.")


# Display results
if model.status == GRB.OPTIMAL:
    print(f"Optimal objective value: {f.X}")
    for v in V:
        for k in range(K):
            if x[v, k].x > 0.5:
                print(f"Vertex {v} is in cluster {k}")
else:
    print("No optimal solution found.")
