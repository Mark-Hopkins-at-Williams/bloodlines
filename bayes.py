from collections import defaultdict
from factor import multiply


class BayesianNetwork:

    def __init__(self, factors):
        self._factors = factors
        self._variables = set()
        for factor in self._factors:
            self._variables = self._variables | set(factor.get_variables())
        self._vars_by_name = {v.get_name(): v for v in self._variables}

    def get_variables(self):
        return self._variables

    def get_variable_by_name(self, var_name):
        return self._vars_by_name[var_name]

    def get_factors(self):
        return self._factors

    def get_factors_with_variable(self, variable):
        return [factor for factor in self._factors
                if variable in factor.get_variables()]

    def moral_graph(self):
        nodes = [var.get_name() for var in self.get_variables()]
        edges = []
        for factor in self._factors:
            vars = [v.get_name() for v in factor.get_variables()]
            for i, var in enumerate(vars):
                edges += [(var, neighbor) for neighbor in vars[:i] + vars[i + 1:]]
        return UndirectedGraph(nodes, edges)

    def reduce(self, evidence):
        reduced_factors = [factor.reduce(evidence) for factor in self._factors]
        return BayesianNetwork(reduced_factors)

    def get_value(self, instantiation):
        g = multiply(self._factors)
        return g.get_value(instantiation)


class UndirectedGraph:

    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.adjacency = defaultdict(set)
        for (node1, node2) in edges:
            self.adjacency[node1].add(node2)
            self.adjacency[node2].add(node1)
        self.adjacency = dict(self.adjacency)

    def get_neighbors(self, node):
        return self.adjacency[node]

    def get_edges(self):
        result = set()
        for node in self.adjacency:
            for neighbor in self.adjacency[node]:
                edge = tuple(sorted([node, neighbor]))
                result.add(edge)
        return sorted(result)

    def __str__(self):
        return str(self.get_edges())

