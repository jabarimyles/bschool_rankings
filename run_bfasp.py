import numpy as np
import pandas as pd
from scipy.optimize import linprog
import cvxpy as cp

import gurobipy as gp
from gurobipy import GRB

# Set NumPy to display floats in fixed-point notation
np.set_printoptions(suppress=True)

def solve_bfasp(weight_matrix):
    """
    Solves the Bidirectional Feedback Arc Set Problem (B-FASP) using a binary linear program with Gurobi.

    Parameters:
    weight_matrix (numpy.ndarray): A square matrix where element (i, j) represents the weight of the arc from node i to node j.

    Returns:
    dict: A solution containing the optimal ranking, the arcs to be removed, and the updated weight matrix.
    """
    n = weight_matrix.shape[0]

    # Create a Gurobi model
    model = gp.Model("B-FASP")

    # Define binary decision variables y_ij
    y = model.addVars(n, n, vtype=GRB.BINARY, name="y")

    # Objective function: minimize the total weight of removed arcs
    model.setObjective(gp.quicksum(weight_matrix[i, j] * (1 - y[i, j]) for i in range(n) for j in range(n) if i != j), GRB.MINIMIZE)

    # Transitivity constraints: y_ij - y_ik - y_kj >= -1 for all distinct i, j, k
    for i in range(n):
        for j in range(n):
            if i != j:
                for k in range(n):
                    if i != k and j != k:  # Ensure all indices are distinct
                        model.addConstr(y[i, j] - y[i, k] - y[k, j] >= -1, name=f"trans_{i}_{j}_{k}")

    # Constraints for bidirectional arcs and ordering
    for i in range(n):
        for j in range(n):
            if i != j:
                if weight_matrix[i, j] > 0 and weight_matrix[j, i] > 0:
                    # Bidirectional arc: y_ij + y_ji >= 1
                    model.addConstr(y[i, j] + y[j, i] >= 1, name=f"bidirectional_{i}_{j}")
                else:
                    # Unidirectional or no arc: y_ij + y_ji = 1
                    model.addConstr(y[i, j] + y[j, i] == 1, name=f"unidirectional_{i}_{j}")

    # Solve the problem
    model.optimize()

    # Extract the solution
    y_sol = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                y_sol[i, j] = y[i, j].X

    removed_arcs = [(i, j) for i in range(n) for j in range(n) if i != j and y_sol[i, j] == 0]

    # Create the updated weight matrix with removed arcs
    updated_weight_matrix = np.copy(weight_matrix)
    for i, j in removed_arcs:
        updated_weight_matrix[i, j] = 0

    return {
        "optimal_value": model.ObjVal,
        "removed_arcs": removed_arcs,
        "ranking_matrix": y_sol,
        "updated_weight_matrix": updated_weight_matrix
    }


def modified_topological_sort(weights, school_names):
    """
    Implements the Modified Topological Sorting Algorithm for unicycle-free graphs as described in the paper.

    Parameters:
        weights (np.array): Adjacency matrix of a unicycle-free graph.
        school_names (list): List of school names corresponding to the matrix indices.

    Returns:
        list: Weak ordering of the nodes with school names.
    """
    n = len(weights)
    visited = [False] * n  # Track visited nodes
    weak_ordering = []  # To store the weak ordering of nodes

    def visit(node):
        """
        Recursive function to visit a node and determine its position in the weak ordering.

        Args:
            node (int): Current node index to process.
        """
        if visited[node]:
            return  # Skip nodes that are already processed

        # Mark the node as visited
        visited[node] = True

        # Step 1: Find the tied nodes (Ξ)
        tied_nodes = {node}  # Start with the current node
        for neighbor in range(n):
            if weights[node, neighbor] > 0 and weights[neighbor, node] > 0:  # Bidirectional arc
                tied_nodes.add(neighbor)

        # Mark all tied nodes as visited to prevent duplicates
        for tied_node in tied_nodes:
            visited[tied_node] = True

        # DEBUG: Log tied nodes (Ξ)
        tied_names = sorted([school_names[tied_node] for tied_node in tied_nodes])
        print(f"Tied Nodes (Ξ): {tied_names}")

        # Step 2: Find the successors of tied nodes (Ω)
        successors = set()
        for tied_node in tied_nodes:
            for neighbor in range(n):
                if (
                    weights[tied_node, neighbor] > 0  # Outgoing edge from tied node
                    and weights[neighbor, tied_node] == 0  # No incoming edge to tied node
                    and neighbor not in tied_nodes  # Not part of tied nodes
                    and not visited[neighbor]  # Not already visited
                ):
                    successors.add(neighbor)

        # DEBUG: Log successor nodes (Ω)
        successor_names = sorted([school_names[successor] for successor in successors])
        print(f"Successors (Ω): {successor_names}")

        # Step 3: Recursively visit all successors
        for successor in successors:
            visit(successor)

        # Step 4: Add the tied nodes to the head of the weak ordering
        weak_ordering.insert(0, tied_names)

        # DEBUG: Log the current weak ordering
        print(f"Weak Ordering (Partial): {weak_ordering}")

    # Perform the modified topological sort for all nodes
    for node in range(n):
        if not visited[node]:
            visit(node)

    return weak_ordering





# Reading the CSV file into a DataFrame
weights = pd.read_csv('Adjacency_Matrix.csv', index_col=0)

# List of school names (from your provided list)
school_names = [
    "Stanford University", "University Pennsylvania", "Northwestern University", "University of Chicago", 
    "Massachusetts Institute of Technology (MIT)", "Harvard University", "New York University", 
    "University of California at Berkeley", "Yale University", "Dartmouth College", "University of Viriginia", 
    "Columbia University", "Duke University", "University of Michigan at Ann Arbor", "Cornell University", 
    "Carnegie Mellon University", "University of Texas at Austin", "Emory University", "University of Southern California", 
    "Indiana University", "University of California at Los Angeles", "University of North Carolina at Chapel Hill", 
    "Vanderbilt University", "Georgetown University", "Georgia Institute of Technology", "Washington University in St. Louis", 
    "University of Georgia", "University of Washington", "Rice University", "Ohio State University", 
    "University of Notre Dame", "Arizona State University", "University of Rochester", "Southern Methodist University", 
    "University of Minnesota at Twin Cities", "University of Florida", "Brigham Young University", 
    "The University of Texas at Dallas", "University of Utah", "William & Mary", "Michigan State University", 
    "University of Maryland at College Park", "University of Wisconsin at Madison", "Texas Christian University", 
    "University of California at Irvine", "Boston College", "Texas A&M University at College Station", 
    "University of Pittsburgh", "University of Tennessee at Knoxville", "Boston University", "Iowa State University", 
    "University of Arizona", "CUNY Bernard M. Baruch College", "Rutgers University at Newark and New Brunswick", 
    "University of Alabama (Manderson)", "University of Houston", "Baylor University", "University of California at Davis", 
    "University of South Carolina", "University of Kansas", "University of Kentucky", "Fordham University", 
    "George Washington University", "Tulane University", "University of Miami", "Case Western Reserve University", 
    "Chapman University", "Lehigh University", "North Carolina State University", "Syracuse University", 
    "University of Colorado at Boulder", "Stevens Institute of Technology", "University of Massachusetts", 
    "University of Buffalo at SUNY", "University of Arkansas at Fayetteville", "Babson College", 
    "Oklahoma State University", "University of California at San Diego", "North Carolina A&T State University", 
    "University of Detroit at Mercy", "Auburn University", "Northeastern University", "University of Mississippi", 
    "University of Oklahoma", "American University", "College of Charleston", "University of Denver", 
    "University South Florida", "Pepperdine University", "Binghamton University at SUNY", 
    "University of California at Riverside", "University of Hawaii at Manoa", "Claremont Graduate University", 
    "Clark Atlanta University", "University of Minnesota at Duluth", "Clark University", "Clarkson University", 
    "Louisiana State University at Baton Rouge", "Louisiana Tech University", "Rochester Institute of Technology", 
    "Saint Louis University"
]

# Filter the DataFrame to only keep rows and columns with indices in the school_names list
filtered_weights = weights.loc[weights.index.isin(school_names), weights.columns.isin(school_names)]
weights_arr = filtered_weights.values
np.fill_diagonal(weights_arr, 0)
# Solve binary program with filtered weights
solution = solve_bfasp(weights_arr)
print("Binary Program Solution:", solution)

# Example Usage
# Perform modified topological sorting on the adjacency matrix
weak_order = modified_topological_sort(solution['updated_weight_matrix'], filtered_weights.index.tolist())
print("Weak Ordering of Universities:")
for rank, group in enumerate(weak_order, start=1):
    print(f"Rank {rank}: {', '.join(group)}")