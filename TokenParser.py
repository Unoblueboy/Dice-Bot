from Tokens import TokenList, TokenType, TokenAssociativity, Token
from collections import deque
from enum import Enum
from typing import Union, List
from pptree import print_tree


class NodeType(Enum):
    LEAF = 1
    ROOT = 2
    INTERNAL = 3


# noinspection PyUnresolvedReferences
class Node(object):
    def __init__(self, token: Token):
        self.token = token
        self.node_type = self._defineNodeType()
        self.token_type = self.token.type
        self._children = deque()

    def _defineNodeType(self):
        if self.token.type in [TokenType.NUMERIC, TokenType.DICE]:
            return NodeType.LEAF
        return NodeType.INTERNAL

    def addChild(self, node):
        self._children.appendleft(node)

    def getChildren(self):
        return self._children

    def eval(self) -> (str, Union[float, List[float]]):
        if self.node_type == NodeType.LEAF:
            out_string, out_value = self.token.eval()
        elif self.token_type != TokenType.FUNCTION:
            result_strings = []
            result_values = []
            for child in self.getChildren():
                res_string, res_value = child.eval()
                result_strings.append(res_string)
                result_values.append(res_value)

            # Pretty Bracket Binary Operators
            if self.token_type == TokenType.BINARY_OPERATOR:
                left_node = self.getChildren()[0]
                right_node = self.getChildren()[1]
                op_token = self.token

                # Left Bracketing
                if left_node.token_type == TokenType.BINARY_OPERATOR:
                    left_token = left_node.token
                    if left_token.precedence < op_token.precedence:
                        result_strings[0] = "({})".format(result_strings[0])
                    elif left_token.precedence == op_token.precedence and \
                            op_token.associativity == TokenAssociativity.RIGHT:
                        result_strings[0] = "({})".format(result_strings[0])

                # Right Bracketing
                if right_node.token_type == TokenType.BINARY_OPERATOR:
                    right_token = right_node.token
                    if right_token.precedence < op_token.precedence:
                        result_strings[1] = "({})".format(result_strings[1])
                    elif right_token.precedence == op_token.precedence and \
                            (not op_token.commutative) and (op_token.associativity != TokenAssociativity.RIGHT):
                        result_strings[1] = "({})".format(result_strings[1])

            out_string, out_value = self.token.eval(result_strings, result_values)
        elif self.token_type == TokenType.FUNCTION:
            if self.token.node_callable:
                out_string, out_value = self.token.eval(self.getChildren())
            else:
                result_strings = []
                result_values = []
                for child in self.getChildren():
                    res_string, res_value = child.eval()
                    result_strings.append(res_string)
                    result_values.append(res_value)
                out_string, out_value = self.token.eval(result_strings, result_values)
        else:
            raise Exception("Unknown Token/ Node Type")

        return out_string, out_value

    def __str__(self):
        return ' '+str(self.token)+' '


class ParseTree(object):
    def __init__(self, input_string):
        self.input_string = input_string.replace(" ", "")
        self.infix_tokens = self._get_tokens(self.input_string)
        self.postfix_tokens = self._shunting_yard(self.infix_tokens)
        self.node_list, self.root = self._generate_parse_tree(self.postfix_tokens)

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

    # Shunting Yard Algorithm as described in the following pages
    # https://wcipeg.com/wiki/Shunting_yard_algorithm
    # https://en.wikipedia.org/wiki/Shunting-yard_algorithm
    @staticmethod
    def _shunting_yard(infix_tokens):
        input_token_queue = deque(infix_tokens)
        output_queue = deque()
        operator_stack = deque()
        arity_stack = deque()

        while len(input_token_queue) > 0:
            token = input_token_queue.popleft()
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
                            (op_token.precedence != token.precedence or
                             token.associativity == TokenAssociativity.RIGHT):
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

    @staticmethod
    def _generate_parse_tree(postfix_tokens):
        evaluation_stack = deque()
        node_list = []

        for token in postfix_tokens:
            new_node = Node(token)
            node_list.append(new_node)

            if new_node.node_type == NodeType.LEAF:
                evaluation_stack.append(new_node)
                continue

            token_type = token.type
            if token_type == TokenType.BINARY_OPERATOR:
                child1 = evaluation_stack.pop()
                child2 = evaluation_stack.pop()
                new_node.addChild(child1)
                new_node.addChild(child2)
                evaluation_stack.append(new_node)
            elif token_type == TokenType.UNARY_OPERATOR:
                child = evaluation_stack.pop()
                new_node.addChild(child)
                evaluation_stack.append(new_node)
            elif token_type == TokenType.FUNCTION:
                arity = token.arity
                for _ in range(arity):
                    child = evaluation_stack.pop()
                    new_node.addChild(child)
                evaluation_stack.append(new_node)
            else:
                raise Exception("Illegal token in postfix_tokens")

        if len(evaluation_stack) != 1:
            raise Exception("Should only be one element left in the Evaluation Stack, the root")

        root = evaluation_stack[0]
        root.node_type = NodeType.ROOT

        return node_list, root

    def evaluate(self):
        res_string, res_value = self.root.eval()
        if (type(res_value) in [int, float]) and (int(res_value) == res_value):
            res_value = int(res_value)
        return res_string, res_value

    def print_tree(self):
        print_tree(self.root, "_children")


if __name__ == "__main__":
    x = ParseTree("max(-2d6+-2d6-2d6, 1+2+3d6!, 23, max(5 + 4, 22d6kh3))")
    print(x.root.token)
    print(x.evaluate())

    x2 = ParseTree("rep(5d6kh3, 6)")
    print(x2.root.token)
    # x2.print_tree()
    print(x2.evaluate())

    x3 = ParseTree("2-1")
    print(x3.root.token)
    # x3.print_tree()
    print(x3.evaluate())

    x4 = ParseTree("(1+2)/(3+4)")
    print(x4.root.token)
    # x4.print_tree()
    print(x4.evaluate())

    x5 = ParseTree("d6")
    print(x5.root.token)
    # x4.print_tree()
    print(x5.evaluate())
