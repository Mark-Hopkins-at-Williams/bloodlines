import unittest
import pandas as pd
from factor import Factor, Variable
from bayes import BayesianNetwork
from elimination import conditional_prob, min_degree_elim_order


def create_example_net():
    p = Variable('P', ['yes', 'no'])
    l = Variable('L', ['u', 'd'])
    s = Variable('S', ['-ve', '+ve'])
    b = Variable('B', ['-ve', '+ve'])
    u = Variable('U', ['-ve', '+ve'])
    p_factor = Factor([p], {
        ('yes',): 0.87,
        ('no',): 0.13})
    l_factor = Factor([p, l], {
        ('yes', 'u'): 0.1,
        ('yes', 'd'): 0.9,
        ('no', 'u'): 0.99,
        ('no', 'd'): 0.01})
    s_factor = Factor([p, s], {
        ('yes', '-ve'): 0.1,
        ('yes', '+ve'): 0.9,
        ('no', '-ve'): 0.99,
        ('no', '+ve'): 0.01})
    b_factor = Factor([l, b], {
        ('u', '-ve'): 0.9,
        ('u', '+ve'): 0.1,
        ('d', '-ve'): 0.3,
        ('d', '+ve'): 0.7})
    u_factor = Factor([l, u], {
        ('u', '-ve'): 0.9,
        ('u', '+ve'): 0.1,
        ('d', '-ve'): 0.2,
        ('d', '+ve'): 0.8})
    return BayesianNetwork([p_factor, l_factor, s_factor, b_factor, u_factor])


class TestElimination(unittest.TestCase):

    def test_variable_elimination(self):
        bnet = create_example_net()
        prob = conditional_prob(bnet, {'P': 'yes'}, {'S': '-ve', 'B': '-ve', 'U': '-ve'})
        self.assertAlmostEqual(prob, .1021, places=4)
        prob = conditional_prob(bnet, {'L': 'u'}, {'S': '-ve', 'B': '-ve', 'U': '-ve'})
        self.assertAlmostEqual(prob, .9585, places=4)


if __name__ == "__main__":
    unittest.main()   