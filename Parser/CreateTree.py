from collections import deque
from typing import List

from Nodes.Token import FunctionToken, Token, TokenType
from Parser.ShuntingYard import shunting_yard
from Parser.TokenParser import get_tokens


def generate_parse_tree(postfix_tokens: List[Token]) -> Token:
    evaluation_stack = deque()

    for token in postfix_tokens:
        if token.type in [TokenType.NUMERIC, TokenType.DICE]:
            evaluation_stack.append(token)
            continue

        token_type = token.type
        if token_type == TokenType.BINARY_OPERATOR:
            right_child = evaluation_stack.pop()
            left_child = evaluation_stack.pop()
            token.addChild(right_child)
            token.addChild(left_child)
            evaluation_stack.append(token)
        elif token_type == TokenType.UNARY_OPERATOR:
            child = evaluation_stack.pop()
            token.addChild(child)
            evaluation_stack.append(token)
        elif token_type == TokenType.FUNCTION:
            token: FunctionToken
            arity = token.arity
            for _ in range(arity):
                child = evaluation_stack.pop()
                token.addChild(child)
            evaluation_stack.append(token)
        else:
            raise Exception("Illegal token in postfix_tokens")

    if len(evaluation_stack) != 1:
        raise Exception("Should only be one element left in the Evaluation Stack, the root")

    root = evaluation_stack[0]

    return root


if __name__ == '__main__':
    print(generate_parse_tree(shunting_yard(get_tokens("5d6 + 1"))).eval())
    print()
    print(generate_parse_tree(shunting_yard(get_tokens("-5d6 - 1 + -2"))).eval())
    print()
    print(generate_parse_tree(shunting_yard(get_tokens("max(d6, 12, 4)"))).eval())
