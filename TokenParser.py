from Tokens import TokenList, TokenType, TokenAssociativity
from collections import deque




# Shunting Yard Algorithm as described in the following pages
# https://wcipeg.com/wiki/Shunting_yard_algorithm
# https://en.wikipedia.org/wiki/Shunting-yard_algorithm


class ParseTree(object):
    def __init__(self, input_string):
        self.input_string = input_string.replace(" ", "")
        infix_tokens = self._get_tokens(input_string)
        postfix_tokens = self._shunting_yard(infix_tokens)

    @staticmethod
    def _get_tokens(input_str):
        input_str = input_str.replace(" ", "")
        tas = TokenList()
        tokens = []

        remaining_string = input_str
        prev_token = None
        while len(remaining_string) > 0:
            # find a matching token and add it to the list tokens
            for token in tas.tokens:
                matches = token.regex.match(remaining_string)
                if not matches:
                    continue

                value, end = matches.group(1, matches.lastindex)

                if value == "-":
                    # Deal with unary minus
                    if (prev_token is None) or prev_token.type in [TokenType.COMMA,
                                                                   TokenType.LEFT_BRACKET,
                                                                   TokenType.BINARY_OPERATOR]:
                        token = tas.getTokenFromName("Unary Minus")

                elif token.type == TokenType.NUMERIC or token.type == TokenType.DICE:
                    # Deal With numeric and dice
                    token = token.copyWithValue(value)

                tokens.append(token)
                prev_token = token
                remaining_string = end
                break
            else:
                raise Exception("Illegal Bitch")

        return tokens

    @staticmethod
    def _shunting_yard(tokens):
        input_token_queue = deque(tokens)
        output_queue = deque()
        operator_stack = deque()
        arity_stack = deque()

        while len(input_token_queue) > 0:
            token = input_token_queue.popleft()
            print(token)
            token_type = token.type
            if token_type in [TokenType.NUMERIC, TokenType.DICE]:
                output_queue.append(token)
            elif token_type == TokenType.FUNCTION:
                arity_stack.append(1)
                operator_stack.append(token)
            elif token_type == TokenType.BINARY_OPERATOR:
                while (len(operator_stack) > 0) and (operator_stack[-1].type not in [TokenType.LEFT_BRACKET]):
                    op_token = operator_stack[-1]
                    if (op_token.precedence <= token.precedence) and \
                            (
                                    op_token.precedence != token.precedence or token.associativity == TokenAssociativity.RIGHT):
                        break
                    op_token = operator_stack.pop()
                    if op_token.type == TokenType.FUNCTION:
                        op_token = op_token.copyWithArity(arity_stack.pop())
                    output_queue.append(op_token)
                operator_stack.append(token)
            elif token_type == TokenType.LEFT_BRACKET:
                operator_stack.append(token)
            elif token_type == TokenType.RIGHT_BRACKET:
                if len(operator_stack) == 0:
                    raise Exception("Mismatched Brackets")

                while operator_stack[-1].type != TokenType.LEFT_BRACKET:
                    op_token = operator_stack.pop()
                    if op_token.type == TokenType.FUNCTION:
                        op_token = op_token.copyWithArity(arity_stack.pop())
                    output_queue.append(op_token)
                    if len(operator_stack) == 0:
                        raise Exception("Mismatched Brackets")

                # discard left bracket
                operator_stack.pop()
                if len(operator_stack) > 0 and operator_stack[-1].type == TokenType.FUNCTION:
                    func_token = operator_stack.pop()
                    func_token = func_token.copyWithArity(arity_stack.pop())
                    output_queue.append(func_token)
            elif token_type == TokenType.UNARY_OPERATOR:
                operator_stack.append(token)
            elif token_type == TokenType.COMMA:
                arity_stack[-1] += 1
                if len(operator_stack) == 0:
                    continue

                while operator_stack[-1].type != TokenType.LEFT_BRACKET:
                    op_token = operator_stack.pop()
                    if op_token.type == TokenType.FUNCTION:
                        op_token = op_token.copyWithArity(arity_stack.pop())
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