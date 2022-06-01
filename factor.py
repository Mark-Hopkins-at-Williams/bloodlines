from variable import instantiations


class Factor:

    def __init__(self, variables, values):
        self._variables = variables
        self._values = values
    
    def get_variables(self):
        return self._variables

    def get_variable(self, name):
        for var in self._variables:
            if var.get_name() == name:
                return var
        return None

    def get_value(self, instantiation):
        key = []
        for var in self._variables:
            if var.get_name() not in instantiation:
                raise Exception('Variable {} not found in given instantiation.'.format(var))
            key.append(instantiation[var.get_name()])
        return self._values[tuple(key)]

    def normalize(self):
        normalizer = sum([v for _, v in self._values.items()])
        return Factor(self._variables, {k: v/normalizer for (k, v) in self._values.items()})

    def reduce(self, evidence):
        reduced_values = dict()
        for event in self._values:
            keep_row = True
            for var, value in zip(self._variables, event):
                if var.get_name() in evidence and evidence[var.get_name()] != value:
                    keep_row = False
            if keep_row:
                reduced_values[event] = self._values[event]
        return Factor(self._variables, reduced_values)

    def sum_out(self, variable):
        if variable not in self._variables:
            raise Exception('Variable {} not found.'.format(variable))
        else:
            variable_index = self._variables.index(variable)
            other_variables = self._variables[0:variable_index] + self._variables[variable_index + 1:]
            new_values = dict()
            for inst in instantiations(other_variables):
                result = 0.0
                for value in variable.get_domain():
                    try:
                        lookup_inst = inst[0:variable_index] + (value,) + inst[variable_index:]
                        result += self._values[lookup_inst]
                    except KeyError:
                        pass
                new_values[inst] = result
            return Factor(other_variables, new_values)

    def __str__(self):
        result = f"{self._variables}:"
        for event, value in self._values.items():
            result += f"\n  {event}: {value}"
        return result

    __repr__ = __str__


def multiply(factors):
    def convert_instantiation_to_dict(variables):
        result = dict()
        for (var, value) in zip(variables, inst):
            result[var.get_name()] = value
        return result
    all_vars = set()
    for factor in factors:
        all_vars = all_vars | set(factor.get_variables())
    all_vars = list(all_vars)
    values = dict()
    for inst in instantiations(all_vars):
        try:
            product = 1.0
            inst_dict = convert_instantiation_to_dict(all_vars)
            for factor in factors:
                product *= factor.get_value(inst_dict)
            values[inst] = product
        except KeyError:
            pass
    return Factor(all_vars, values)
        
