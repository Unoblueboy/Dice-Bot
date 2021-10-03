import unittest
from unittest import TestCase

from TokenParser import ParseTree


class TestParse(unittest.TestCase):
    def test_node(self):
        assert True

    def test_parse_tree(self):
        with open("cases.txt", "r") as file:
            lines = file.readlines()
        num_subtests = len(lines)
        for i in range(num_subtests):
            str_input, exp_output = lines[i].split(", ")
            pt = ParseTree(str_input.strip())
            out_str, _ = pt.evaluate()
            with self.subTest(i=i+1):
                self.assertEqual(out_str, exp_output.strip())
