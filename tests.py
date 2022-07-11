import unittest
from evaluation import *
from sklearn.metrics.cluster import rand_score
from utils import *

class TestWorkflow(unittest.TestCase):
    def test_connect1(self):
        lst = [(1,4), (5,4), (2,3), (3,6), (1,7)]
        result = connect("", lst)
        self.assertEqual(set(result[1]), set([1,4,5,7]))
        self.assertEqual(set(result[2]), set([2, 3, 6]))
    
    def test_evaluate_components1(self):
        true_names = {"A":1, "B":2, "C":3}
        predicted_names = {"A": 2, "B":3, "C":4}
        self.assertEqual(evaluate_components(true_names, predicted_names), [0, 3, 0, 0])

    def test_evaluate_components2(self):
        true_names = {"A":2, "B":2, "C":3, "D":4}
        predicted_names = {"A": 1, "B":3, "C":4, "D":4}
        self.assertEqual(evaluate_components(true_names, predicted_names), [0, 4, 1, 1])
    
    def test_evaluate_components3(self):
        true_names = {"A":2, "B":2, "C":3, "D":4, "E":2, "F":4, "G":10}
        predicted_names = {"A": 1, "B":3, "C":4, "D":4, "E":3, "F":4, "G": 20}
        tp = evaluate_components(true_names, predicted_names)[0]
        tn = evaluate_components(true_names, predicted_names)[1]
        fp = evaluate_components(true_names, predicted_names)[2]
        fn = evaluate_components(true_names, predicted_names)[3]
        self.assertEqual(rand_score(list(true_names.values()), list(predicted_names.values())), (tp + tn) / (tp + tn + fp + fn))

    def test_tuple_to_list(self):
        lst = [1,2,3,4,5]
        tuples = [(1,2), (3,4), (4,5)]
        self.assertEqual(list_to_tuple(lst), tuples)

        lst2 = [1,2,3,4]
        tuples2 = [(1,2), (3,4)]
        self.assertEquals(list_to_tuple(lst2), tuples2)