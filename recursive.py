import networkx as nx
import matplotlib.pyplot as plt
import random
import gurobipy as gp
from gurobipy import GRB
import networkx as nx
import itertools

def generate_tournament_graph(num_nodes):
    """
    Generate a random tournament graph with `num_nodes` nodes.
    Each pair of nodes has exactly one directed edge between them.
    """
    G = nx.DiGraph()
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if random.random() > 0.5:
                G.add_edge(i, j, weight=random.randint(1, 10))
                if random.random() > 0.75:
                    G.add_edge(j, i, weight=random.randint(1, 10))
            else:
                G.add_edge(j, i, weight=random.randint(1, 10))
                if random.random() > 0.75:
                    G.add_edge(i, j, weight=random.randint(1, 10))
    return G

def solve_lp_relaxation(G):
    """
    Solve the LP relaxation of the B-FASP problem using Gurobi.
    Args:
        G: A tournament graph (DiGraph) with weights on edges.
    Returns:
        A tuple containing:
        - The relaxed objective value.
        - The fractional solution as a dictionary {(i, j): y_ij}.
    """
    model = gp.Model("B-FASP_LP")

    # Create decision variables y_ij
    y = {}
    for u, v in G.edges():
        y[u, v] = model.addVar(lb=0, ub=1, vtype=GRB.CONTINUOUS, name=f"y_{u}_{v}")
        y[v, u] = model.addVar(lb=0, ub=1, vtype=GRB.CONTINUOUS, name=f"y_{v}_{u}")

    # Objective: Minimize the total weight of removed arcs
    model.setObjective(
        gp.quicksum(G[u][v]["weight"] * (1 - y[u, v]) for u, v in G.edges()), GRB.MINIMIZE
    )

    # Constraints
    for u, v in G.edges():
        # Ordering constraint: y_ij + y_ji = 1
        model.addConstr(y[u, v] + y[v, u] == 1, f"ordering_{u}_{v}")

    for i, j, k in itertools.permutations(G.nodes, 3):
        # Transitivity constraint: y_ij - y_ik - y_kj >= -1
        model.addConstr(y[i, j] - y[i, k] - y[k, j] >= -1, f"transitivity_{i}_{j}_{k}")

    # Solve the LP relaxation
    model.optimize()

    if model.status == GRB.OPTIMAL:
        objective_value = model.objVal
        solution = {(u, v): y[u, v].X for u, v in y}
        return objective_value, solution
    else:
        raise Exception("Optimal solution not found!")

def enumerate_all_solutions(G):
    """
    Enumerate all possible acyclic orderings of the graph to find the exact optimal solution.
    Group edges by the cycle they are part of and only remove edges that exist in the graph.
    Args:
        G: A tournament graph (DiGraph) with weights on edges.
    Returns:
        A tuple containing:
        - The exact objective value.
        - The corresponding feedback arc set grouped by cycles.
    """
    nodes = list(G.nodes)
    best_cost = float("inf")
    best_feedback_set = None

    # Enumerate all possible orderings
    for perm in itertools.permutations(nodes):
        # Create a copy of the graph and initialize the feedback set
        graph_copy = G.copy()
        feedback_set = set()

        # Find all unique cycles and group edges
        unique_cycles = find_unique_cycles_with_edges(graph_copy)
        for cycle_edges in unique_cycles:
            for u, v in cycle_edges:
                # Only remove edges that actually exist in the graph
                if graph_copy.has_edge(u, v) and perm.index(u) > perm.index(v):  # Backward edge
                    feedback_set.add((u, v))
                    graph_copy.remove_edge(u, v)

        # Check if the resulting graph is acyclic
        if is_acyclic(graph_copy):
            # Calculate the cost of removing the feedback arcs
            cost = sum(G[u][v]["weight"] for u, v in feedback_set)

            # Update best solution if this is better
            if cost < best_cost:
                best_cost = cost
                best_feedback_set = feedback_set

    return best_cost, best_feedback_set


def is_acyclic(graph):
    """
    Check if the graph is acyclic.
    """
    try:
        nx.find_cycle(graph, orientation="original")
        return False
    except nx.NetworkXNoCycle:
        return True

def find_unique_cycles_with_edges(graph):
    """
    Identify all unique cycles in the graph and group edges by the cycle they are part of.
    Args:
        graph: A directed graph (DiGraph).
    Returns:
        A list of unique cycles, where each cycle is represented as a list of edges.
    """
    unique_cycles = set()
    try:
        # Find all simple cycles using networkx's built-in function
        simple_cycles = list(nx.simple_cycles(graph))
        for cycle in simple_cycles:
            # Standardize the cycle by sorting it (rotating to start at the smallest node)
            rotated_cycle = min([cycle[i:] + cycle[:i] for i in range(len(cycle))])
            # Convert nodes in the cycle to a tuple of sorted edges
            edges_in_cycle = tuple((rotated_cycle[i], rotated_cycle[(i + 1) % len(rotated_cycle)]) 
                                   for i in range(len(rotated_cycle)))
            unique_cycles.add(edges_in_cycle)
    except nx.NetworkXNoCycle:
        pass
    return list(unique_cycles)


def recursive_dominance_ordering(G):
    """
    Implement the recursive dominance ordering approach for tournament graphs.
    Args:
        G: A tournament graph (DiGraph) with weights on edges.
    Returns:
        A tuple containing:
        - The ordering of nodes.
        - The set of removed arcs for the feedback arc set.
    """
    feedback_arc_set = set()
    ordering = []

    # Work on a copy of the graph to preserve the original
    H = G.copy()

    while len(H.nodes) > 0:
        # Select the node with the highest out-degree minus in-degree
        dominance = {node: H.out_degree(node) - H.in_degree(node) for node in H.nodes}
        dominant_node = max(dominance, key=dominance.get)
        ordering.append(dominant_node)
        H.remove_node(dominant_node)

    # Identify backward arcs in the ordering
    node_index = {node: idx for idx, node in enumerate(ordering)}
    for u, v, data in G.edges(data=True):
        if node_index[u] > node_index[v]:  # Backward arc
            feedback_arc_set.add((u, v))

    return ordering, feedback_arc_set

def plot_tournament_graph(G, title="Tournament Graph"):
    """
    Plot the given tournament graph.
    """
    pos = nx.circular_layout(G)  # Layout for better visualization of tournaments
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=2000, font_size=15, font_weight="bold")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red")
    plt.title(title)
    plt.show()


def main():
    # Generate a random tournament graph
    num_nodes = 50  # Adjust the number of nodes as needed
    tournament_graph = generate_tournament_graph(num_nodes)

    # Plot the original tournament graph
    plot_tournament_graph(tournament_graph, title="Original Tournament Graph")

    # Solve the LP relaxation
    print("Solving LP relaxation...")
    lp_value, lp_solution = solve_lp_relaxation(tournament_graph)
    print("LP Objective Value:", lp_value)

    # Enumerate all solutions for exact optimal
    print("Enumerating all possible solutions...")
    cycles = find_unique_cycles_with_edges(tournament_graph)
    exact_value, exact_feedback_set = enumerate_all_solutions(tournament_graph)
    print("Exact Objective Value:", exact_value)
    print("Exact Feedback Arc Set:", exact_feedback_set)

if __name__ == "__main__":
    main()



    # Apply the recursive dominance ordering algorithm
    ordering, feedback_arc_set = recursive_dominance_ordering(tournament_graph)

    # Print the results
    print("Ordering of nodes:", ordering)
    print("Feedback arc set (arcs to remove):", feedback_arc_set)

    # Highlight the feedback arc set in the graph
    feedback_graph = tournament_graph.copy()
    feedback_graph.remove_edges_from(feedback_arc_set)

    # Plot the resulting acyclic graph after removing the feedback arc set
    plot_tournament_graph(feedback_graph, title="Acyclic Graph After Removing Feedback Arc Set")
