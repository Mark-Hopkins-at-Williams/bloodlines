class Variable:
    """A variable and its domain."""
    
    def __init__(self, name, domain):
        self._name = name
        self._domain = tuple(domain)
        
    def get_name(self):
        return self._name
    
    def get_domain(self):
        return self._domain
    
    def __hash__(self):
        return hash(self._name)

    def __lt__(self, other):
        return self._name < other.get_name()

    def __repr__(self):
        return self._name

    def __str__(self):
        return self._name
    
    def __eq__(self, other):
        return other.get_name() == self._name and other.get_domain() == self._domain


def instantiations(vars):
    """
    Takes a list of variables and returns the cross-product of the domains.
    
    For instance, suppose the domain of variable X is ('a', 'b') and the
    domain of the variable Y is ('c','d','e'). Then:
        
       >>> X = Variable('X', ('a', 'b'))
       >>> Y = Variable('Y', ('c', 'd', 'e'))
       >>> instantiations([X, Y])
       [('a', 'c'), ('a', 'd'), ('a', 'e'), ('b', 'c'), ('b', 'd'), ('b', 'e')]
    
    """
    def instantiations_helper(variables):
        if len(variables) == 0:
            return [()]
        if len(variables) == 1:
            return [[v] for v in variables[0].get_domain()]
        else:
            first_var = variables[0]
            other_instantiations = instantiations_helper(variables[1:])
            result = []
            for value in first_var.get_domain():
                for inst in other_instantiations:
                    result.append([value] + inst)
            return result
    return [tuple(i) for i in instantiations_helper(vars)]
    