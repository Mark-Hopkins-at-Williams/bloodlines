from factor import multiply
from bayes import BayesianNetwork


def min_degree_elim_order(moral_graph):
    def min_degree_node(adjacency):
        best, best_degree = None, float("inf")
        for node in adjacency:
            if len(adjacency[node]) < best_degree:
                best, best_degree = node, len(adjacency[node])
        return best
    adjacencies = moral_graph.adjacency
    elim_order = []
    while len(adjacencies) > 0:
        min_degree = min_degree_node(adjacencies)
        adjacencies = {n: adjacencies[n] - {min_degree} for n in adjacencies if n != min_degree}
        elim_order.append(min_degree)
    return elim_order


def eliminate(bnet, var_name):
    variable = bnet.get_variable_by_name(var_name)
    relevant = []
    irrelevant = []
    for factor in bnet.get_factors():
        if variable in factor.get_variables():
            relevant.append(factor)
        else:
            irrelevant.append(factor)
    new_factor = multiply(relevant)
    new_factor = new_factor.sum_out(variable)
    return BayesianNetwork(irrelevant + [new_factor])


def variable_elimination(bnet, evidence, elim_order):
    bnet = bnet.reduce(evidence)
    while len(elim_order) > 0:
        var, elim_order = elim_order[0], elim_order[1:]
        if var not in evidence.keys():
            bnet = eliminate(bnet, var)
    return bnet.get_value(evidence)


def conditional_prob(bnet, event, evidence):
    event_and_evidence = {**event, **evidence}
    elim_order = min_degree_elim_order(bnet.moral_graph())
    numerator = variable_elimination(bnet, event_and_evidence, elim_order)
    denominator = variable_elimination(bnet, evidence, elim_order)
    return numerator / denominator
        
