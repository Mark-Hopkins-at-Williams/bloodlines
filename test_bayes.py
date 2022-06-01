import unittest
import pandas as pd
from factor import Variable, Factor
from bayes import BayesianNetwork


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


class TestBayes(unittest.TestCase):

    def test_moral_graph1(self):
        bnet = create_example_net()
        moral_graph = bnet.moral_graph()
        self.assertEqual(moral_graph.get_edges(),
                         [('B', 'L'), ('L', 'P'), ('L', 'U'), ('P', 'S')])





if __name__ == "__main__":
    unittest.main()   