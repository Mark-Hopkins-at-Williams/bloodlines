import unittest
import pandas as pd
from variable import Variable
from factor import Factor, multiply


def example_factors():
    p = Variable('P', ['yes', 'no'])
    l = Variable('L', ['u', 'd'])
    p_factor = Factor([p], {
        ('yes',): 0.87,
        ('no',): 0.13})
    l_factor = Factor([p, l], {
        ('yes', 'u'): 0.1,
        ('yes', 'd'): 0.9,
        ('no', 'u'): 0.99,
        ('no', 'd'): 0.01})
    return p_factor, l_factor


class TestBayes(unittest.TestCase):

    def test_get_variables(self):
        p_factor, l_factor = example_factors()
        self.assertEqual(p_factor.get_variables(), [Variable('P', ['yes', 'no'])])
        self.assertEqual(set(l_factor.get_variables()), set([Variable('P', ['yes', 'no']),
                                                             Variable('L', ['u', 'd'])], ))
        self.assertEqual(l_factor.get_variable('L'), Variable('L', ['u', 'd']))
        self.assertEqual(l_factor.get_variable('P'), Variable('P', ['yes', 'no']))

    def test_get_value(self):
        _, l_factor = example_factors()
        self.assertEqual(l_factor.get_value({'P': 'yes', 'L': 'u'}), .1)
        self.assertEqual(l_factor.get_value({'P': 'yes', 'L': 'd'}), .9)
        self.assertEqual(l_factor.get_value({'P': 'no', 'L': 'u'}), .99)
        self.assertEqual(l_factor.get_value({'P': 'no', 'L': 'd'}), .01)

    def test_normalize(self):
        _, l_factor = example_factors()
        l_factor = l_factor.normalize()
        self.assertEqual(l_factor.get_value({'P': 'yes', 'L': 'u'}), .05)
        self.assertEqual(l_factor.get_value({'P': 'yes', 'L': 'd'}), .45)
        self.assertEqual(l_factor.get_value({'P': 'no', 'L': 'u'}), .495)
        self.assertEqual(l_factor.get_value({'P': 'no', 'L': 'd'}), .005)

    def test_reduce(self):
        _, l_factor = example_factors()
        l_factor = l_factor.reduce({'P': 'yes'})
        self.assertEqual(l_factor.get_value({'P': 'yes', 'L': 'u'}), .1)
        self.assertEqual(l_factor.get_value({'P': 'yes', 'L': 'd'}), .9)
        with self.assertRaises(KeyError):
            l_factor.get_value({'P': 'no', 'L': 'u'})
        with self.assertRaises(KeyError):
            l_factor.get_value({'P': 'no', 'L': 'd'})

    def test_sum_out(self):
        _, l_factor = example_factors()
        factor = l_factor.sum_out(Variable('L', ['u', 'd']))
        self.assertEqual(factor.get_value({'P': 'yes'}), 1.0)
        self.assertEqual(factor.get_value({'P': 'no'}), 1.0)
        factor = l_factor.sum_out(Variable('P', ['yes', 'no']))
        self.assertEqual(factor.get_value({'L': 'u'}), 1.09)
        self.assertEqual(factor.get_value({'L': 'd'}), .91)

    def test_multiply(self):
        p_factor, l_factor = example_factors()
        product = multiply([p_factor, l_factor])
        self.assertAlmostEqual(product.get_value({'P': 'yes', 'L': 'u'}), .087)
        self.assertAlmostEqual(product.get_value({'P': 'yes', 'L': 'd'}), .783)
        self.assertAlmostEqual(product.get_value({'P': 'no', 'L': 'u'}), .1287)
        self.assertAlmostEqual(product.get_value({'P': 'no', 'L': 'd'}), .0013)


if __name__ == "__main__":
    unittest.main()   