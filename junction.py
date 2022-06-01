from collections import defaultdict
import numpy as np
from scipy.sparse.csgraph import minimum_spanning_tree
from factor import multiply
from elimination import min_degree_elim_order
from bayes import UndirectedGraph


def build_junction_tree(moral_graph, elim_order):
    def elimination_cliques():
        result = []
        adjacencies = moral_graph.adjacency
        for node in elim_order:
            result.append(adjacencies[node] | {node})
            neighbors = adjacencies[node]
            new_adjacencies = dict()
            for n in adjacencies:
                if n in neighbors:
                    new_adjacencies[n] = (adjacencies[n] - {node}) | (neighbors - {n})
                elif n != node:
                    new_adjacencies[n] = adjacencies[n]
            adjacencies = new_adjacencies
        return result
    cliques = elimination_cliques()
    adjacency_matrix = np.zeros((len(cliques), len(cliques)), int)
    for i in range(len(cliques)):
        for j in range(i+1, len(cliques)):
            adjacency_matrix[i][j] = -len(cliques[i] & cliques[j])
    mst = minimum_spanning_tree(adjacency_matrix)
    edges = zip(mst.nonzero()[0], mst.nonzero()[1])
    graph = UndirectedGraph(nodes=list(range(len(elim_order))), edges=edges)
    return JunctionTree(graph, cliques)


def build_junction_tree_for_bayes_net(bnet):
    moral_graph = bnet.moral_graph()
    elim_order = min_degree_elim_order(moral_graph)
    junction_tree = build_junction_tree(moral_graph, elim_order)
    for factor in bnet.get_factors():
        junction_tree.add_factor(factor)
    return junction_tree


class JunctionTree:

    def __init__(self, graph, clusters):
        self.graph = graph
        self.clusters = clusters
        self.node_map = defaultdict(set)
        for node, cluster in enumerate(self.clusters):
            for variable in cluster:
                self.node_map[variable].add(node)
        self.node_map = dict(self.node_map)
        self.factors = dict()
        for node in self.graph.nodes:
            self.factors[node] = []

    def add_factor(self, factor):
        nodesets = [self.node_map[var.get_name()] for var in factor.get_variables()]
        possible_assignments = nodesets[0]
        for nodeset in nodesets[1:]:
            possible_assignments = possible_assignments & nodeset
        assignment = list(possible_assignments)[0]
        self.factors[assignment].append(factor)

    def init_message_queue(self):
        order = []
        frontier = [(0, n) for n in self.graph.get_neighbors(0)]
        while len(frontier) > 0:
            (src, dest), frontier = frontier[0], frontier[1:]
            frontier = frontier + [(dest, n) for n in self.graph.get_neighbors(dest) - {src}]
            order.append((src, dest))
        order = [(dest, src) for (src, dest) in order[::-1]] + order
        return order

    def __str__(self):
        result = str(self.graph)
        for node in self.graph.nodes:
            result += f'\n** node {node} : {self.clusters[node]} **'
            if len(self.factors[node]) > 0:
                result += '\n'
                result += '\n'.join([str(f) for f in self.factors[node]])
        return result


class BeliefPropagation:

    def __init__(self, junction_tree):
        self.junction_tree = junction_tree
        self.messages = None
        self.factors = None

    def run(self, evidence):
        self.factors = {node: [f.reduce(evidence) for f in self.junction_tree.factors[node]]
                        for node in self.junction_tree.factors}
        edges = self.junction_tree.init_message_queue()
        messages = dict()
        for (src, dest) in edges:
            factors_to_multiply = [f for f in self.factors[src]]
            for neighbor in self.junction_tree.graph.get_neighbors(src):
                if neighbor != dest:
                    factors_to_multiply.append(messages[(neighbor, src)])
            message = multiply(factors_to_multiply)
            for v in message.get_variables():
                if v.get_name() not in self.junction_tree.clusters[dest]:
                    message = message.sum_out(v)
            messages[(src, dest)] = message
        self.messages = messages

    def get_marginals(self):
        marginals = defaultdict(list)
        for edge in self.messages:
            marginals[edge[1]].append(self.messages[edge])
        for node in marginals:
            marginals[node] += self.factors[node]
            marginals[node] = multiply(marginals[node])
            for variable in marginals[node].get_variables():
                if variable.get_name() not in self.junction_tree.clusters[node]:
                    marginals[node] = marginals[node].sum_out(variable)
        single_var_marginals = dict()
        for node in marginals:
            for variable in marginals[node].get_variables():
                if variable.get_name() not in single_var_marginals:
                    single_var_marginals[variable.get_name()] = marginals[node]
        for var in single_var_marginals:
            for other in single_var_marginals[var].get_variables():
                if other.get_name() != var:
                    single_var_marginals[var] = single_var_marginals[var].sum_out(other)
        return {var: single_var_marginals[var].normalize() for var in single_var_marginals}


