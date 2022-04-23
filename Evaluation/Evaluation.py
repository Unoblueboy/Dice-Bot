from typing import Tuple

from Nodes.Token import NumericToken, validateNumericEval
from Parser.CreateTree import generate_parse_tree
from Parser.ShuntingYard import shunting_yard
from Parser.TokenParser import get_tokens


def evaluate_roll_string(roll_string: str) -> Tuple[str, object]:
    infix_tokens = get_tokens(roll_string)
    postfix_tokens = shunting_yard(infix_tokens)
    root_token = generate_parse_tree(postfix_tokens)
    result_strings, result_tokens = root_token.eval()
    validateNumericEval(result_strings, result_tokens)
    # noinspection PyTypeChecker
    result_token: NumericToken = result_tokens[0]
    result_string = result_strings[0]
    return result_string, result_token.value


if __name__ == '__main__':
    print(evaluate_roll_string("5d6 + 1"))
    print()
    print(evaluate_roll_string("-5d6 - 1 + -2"))
    print()
    print(evaluate_roll_string("max(d6, 12, d8)"))
