from collections import deque
from typing import List

from Nodes.Token import BinaryOperatorToken, NonNumericToken, FunctionToken, Token, TokenAssociativity, TokenType

from Parser.TokenParser import get_tokens


# Shunting Yard Algorithm as described in the following pages
# https://wcipeg.com/wiki/Shunting_yard_algorithm
# https://en.wikipedia.org/wiki/Shunting-yard_algorithm
def shunting_yard(infix_tokens: List[Token]):
    input_token_queue = deque(infix_tokens)
    output_queue = deque()
    operator_stack = deque()
    arity_stack = deque()

    while len(input_token_queue) > 0:
        token: Token = input_token_queue.popleft()
        token_type = token.type
        if token_type in [TokenType.NUMERIC, TokenType.DICE]:
            output_queue.append(token)
        elif token_type == TokenType.FUNCTION:
            arity_stack.append(1)
            operator_stack.append(token)
        elif token_type == TokenType.BINARY_OPERATOR:
            token: BinaryOperatorToken
            while (len(operator_stack) > 0) and (operator_stack[-1].type not in [TokenType.LEFT_BRACKET]):
                op_token: NonNumericToken = operator_stack[-1]
                if (op_token.precedence <= token.precedence) and \
                        (op_token.precedence != token.precedence or
                         token.associativity == TokenAssociativity.RIGHT):
                    break
                op_token = operator_stack.pop()
                if op_token.type == TokenType.FUNCTION:
                    op_token: FunctionToken
                    op_token.arity = arity_stack.pop()
                output_queue.append(op_token)
            operator_stack.append(token)
        elif token_type == TokenType.LEFT_BRACKET:
            operator_stack.append(token)
        elif token_type == TokenType.RIGHT_BRACKET:
            if len(operator_stack) == 0:
                raise Exception("Mismatched Brackets")

            while operator_stack[-1].type != TokenType.LEFT_BRACKET:
                op_token: NonNumericToken = operator_stack.pop()
                if op_token.type == TokenType.FUNCTION:
                    op_token: FunctionToken
                    op_token.arity = arity_stack.pop()
                output_queue.append(op_token)
                if len(operator_stack) == 0:
                    raise Exception("Mismatched Brackets")

            # discard left bracket
            operator_stack.pop()
            if len(operator_stack) > 0 and operator_stack[-1].type == TokenType.FUNCTION:
                func_token: FunctionToken
                func_token = operator_stack.pop()
                func_token.arity = arity_stack.pop()
                output_queue.append(func_token)
        elif token_type == TokenType.UNARY_OPERATOR:
            operator_stack.append(token)
        elif token_type == TokenType.COMMA:
            arity_stack[-1] += 1
            if len(operator_stack) == 0:
                continue

            while operator_stack[-1].type != TokenType.LEFT_BRACKET:
                op_token: NonNumericToken = operator_stack.pop()
                if op_token.type == TokenType.FUNCTION:
                    op_token: FunctionToken
                    op_token.arity = arity_stack.pop()
                output_queue.append(op_token)
                if len(operator_stack) == 0:
                    raise Exception("Mismatched Brackets")
        else:
            raise Exception("Unknown Token Type")

    while len(operator_stack) > 0:
        op_token = operator_stack.pop()
        if op_token.type in [TokenType.LEFT_BRACKET, TokenType.RIGHT_BRACKET]:
            raise Exception("Mismatched Brackets")
        output_queue.append(op_token)

    return output_queue


if __name__ == '__main__':
    print(shunting_yard(get_tokens("5d6 + 1")))
    print()
    print(shunting_yard(get_tokens("-5d6 - 1 + -2")))
    print()
    print(shunting_yard(get_tokens("max(d6, 12, d8)")))
