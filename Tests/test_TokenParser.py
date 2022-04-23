import unittest

from Evaluation.Evaluation import evaluate_roll_string


class TestParse(unittest.TestCase):
    def test_node(self):
        assert True

    def test_parse_tree_2(self):
        with open("cases.txt", "r") as file:
            lines = file.readlines()
        num_subtests = len(lines)
        for i in range(num_subtests):
            str_input, exp_output = lines[i].split(", ")
            out_str, _ = evaluate_roll_string(str_input.strip())
            with self.subTest(i=i+1):
                self.assertEqual(out_str, exp_output.strip())
