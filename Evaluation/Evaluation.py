from typing import Tuple

from Nodes.Token import NumericToken, Token, validateNumericEvalList
from Parser.CreateTree import generate_parse_tree
from Parser.ShuntingYard import shunting_yard
from Parser.TokenParser import get_tokens


def evaluate_roll_string(roll_string: str) -> Tuple[str, object]:
    infix_tokens = get_tokens(roll_string)
    postfix_tokens = shunting_yard(infix_tokens)
    root_token = generate_parse_tree(postfix_tokens)
    result_tokens: Tuple[Token, ...]
    result_strings, result_tokens = root_token.eval()
    validateNumericEvalList(result_strings, result_tokens)
    result_tokens: Tuple[NumericToken, ...]

    if len(result_strings) == 1:
        result_string = result_strings[0]
    else:
        result_string = "[" + ", ".join(result_strings) + "]"

    if len(result_tokens) == 1:
        result_token: NumericToken = result_tokens[0]
        result_value = result_token.value
    else:
        result_value = [token.value for token in result_tokens]

    return result_string, result_value


if __name__ == '__main__':
    print(evaluate_roll_string("5d6 + 1"))
    print()
    print(evaluate_roll_string("-5d6 - 1 + -2"))
    print()
    print(evaluate_roll_string("max(d6, 12, d8)"))
    print()
    print(evaluate_roll_string("min(rep(6d6, 6), -100)"))
