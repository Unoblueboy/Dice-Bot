import unittest

from Nodes.Token import NumericToken, Token, TokenType, ValueToken


def generate_token_equality_test_cases():
    return [
        ("Generic Token Equality", Token("token", TokenType.NUMERIC), Token("token", TokenType.NUMERIC), True),
        ("Generic Token Equality", Token("token", TokenType.NUMERIC), Token("token", TokenType.DICE), False),
        ("Generic Token Equality", Token("token1", TokenType.NUMERIC), Token("token2", TokenType.NUMERIC), False),
        (
            "Value Token Equality",
            ValueToken("num", TokenType.NUMERIC, 2),
            ValueToken("num", TokenType.NUMERIC, 2),
            True
        ),
        (
            "Value Token Inequality 1",
            ValueToken("num", TokenType.NUMERIC, 1),
            ValueToken("num", TokenType.NUMERIC, 2),
            False
        ),
        (
            "Value Token Inequality 2",
            ValueToken("num", TokenType.DICE, 2),
            ValueToken("num", TokenType.NUMERIC, 2),
            False
        ),
        (
            "Value Token Inequality 3",
            ValueToken("num 1", TokenType.NUMERIC, 2),
            ValueToken("num 2", TokenType.NUMERIC, 2),
            False
        ),
    ]


class TestTokens(unittest.TestCase):
    def test_ValueTokenEquality(self):
        test_cases = generate_token_equality_test_cases()
        for case_name, token1, token2, expected_equal in test_cases:
            with self.subTest(msg=case_name):
                if expected_equal:
                    self.assertEqual(token1, token2)
                else:
                    self.assertNotEqual(token1, token2)
