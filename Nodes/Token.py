import abc
from enum import Enum
from typing import Callable, Generic, List, Tuple, TypeVar

from Dice import Dice


class TokenType(Enum):
    NUMERIC = 1
    DICE = 2
    BINARY_OPERATOR = 3
    UNARY_OPERATOR = 4
    FUNCTION = 5
    LEFT_BRACKET = 6
    RIGHT_BRACKET = 7
    COMMA = 8


class TokenAssociativity(Enum):
    LEFT = 1
    RIGHT = 2


class Token(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self,
                 name: str,
                 token_type: TokenType):
        super(Token, self).__init__()
        self.name = name
        self.type = token_type
        self._children: List["Token", ...] = []

    @abc.abstractmethod
    def eval(self) -> Tuple[Tuple[str, ...], Tuple["Token", ...]]:
        """Method documentation"""
        raise NotImplementedError("The method eval was not implemented")

    def addChild(self, token: "Token"):
        self._children.insert(0, token)

    def getChildren(self) -> List["Token"]:
        return self._children

    def __repr__(self):
        additional_repr = self.__get_additional_repr__()
        if len(additional_repr) > 0:
            return f"<[{self.__class__.__name__}] name: {self.name}, type: {self.type.name}, {additional_repr}>"
        else:
            return f"<[{self.__class__.__name__}] name: {self.name}, type: {self.type.name}>"

    def __get_additional_repr__(self) -> str:
        return ""

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Token):
            return (self.name == other.name) and (self.type == other.type)
        return False


V = TypeVar('V')


class ValueToken(Token, Generic[V]):
    def __init__(self,
                 name: str,
                 token_type: TokenType,
                 value: V):
        super(ValueToken, self).__init__(name, token_type)
        self.value: V = value

    def eval(self) -> Tuple[Tuple[str, ...], Tuple["Token", ...]]:
        raise NotImplementedError()

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, ValueToken):
            return (self.name == other.name) and (self.type == other.type) and (self.value == other.value)
        return False

    def __get_additional_repr__(self):
        s = f"value: {self.value}"
        return s

    def __str__(self):
        if self.value is None:
            return "None"
        return self.value


class NumericToken(ValueToken[float]):
    def __init__(self,
                 name: str,
                 value: float):
        super(NumericToken, self).__init__(name, TokenType.NUMERIC, value)

    def eval(self) -> Tuple[Tuple[str, ...], Tuple["Token", ...]]:
        result_node = NumericToken("num", self.value)
        return (str(self.value),), (result_node,)


class DiceToken(ValueToken[str]):
    def __init__(self,
                 name: str,
                 value: str):
        super(DiceToken, self).__init__(name, TokenType.DICE, value)
        self.dice = Dice(value)

    def eval(self) -> Tuple[Tuple[str, ...], Tuple["Token", ...]]:
        values, token_str = self.dice.roll()
        result_node = NumericToken(self.value, sum(values))
        return (token_str,), (result_node,)


class NonValueToken(Token):
    def __init__(self,
                 name: str,
                 token: str,
                 associativity: TokenAssociativity,
                 precedence: int,
                 token_type: TokenType):
        super(NonValueToken, self).__init__(name, token_type)
        self.token = token
        self.associativity = associativity
        self.precedence = precedence

    def eval(self) -> Tuple[Tuple[str, ...], Tuple["Token", ...]]:
        raise NotImplementedError("eval not implemented")

    def __get_additional_repr__(self) -> str:
        s = f"token: {self.token},associativity: {self.associativity.name}, precedence: {self.precedence}"
        return s

    def __str__(self):
        return self.token


class BinaryOperatorToken(NonValueToken):
    def __init__(self,
                 name: str,
                 token: str,
                 associativity: TokenAssociativity,
                 precedence: int,
                 eval_function: Callable[[Tuple[str, ...], Tuple["NumericToken", ...]],
                                         Tuple[Tuple[str, ...], Tuple["Token", ...]]],
                 commutative: bool = True
                 ):
        super(BinaryOperatorToken, self).__init__(name,
                                                  token,
                                                  associativity,
                                                  precedence,
                                                  TokenType.BINARY_OPERATOR)
        self.eval_function = eval_function
        self.commutative = commutative

    def eval(self) -> Tuple[Tuple[str, ...], Tuple["Token", ...]]:
        result_strings: List[str] = []
        result_values: List["NumericToken"] = []
        children = self.getChildren()
        if len(children) != 2:
            raise ValueError(f"{self} has {len(children)} children, 2 expected")
        for child in children:
            res_strings, res_tokens = child.eval()
            validateNumericEval(res_strings, res_tokens)
            result_strings += res_strings
            result_values += res_tokens

        # Pretty Bracket Binary Operators
        left_token: Token = children[0]
        right_token: Token = children[1]
        op_token = self

        # Left Bracketing
        if left_token.type == TokenType.BINARY_OPERATOR:
            left_token: BinaryOperatorToken
            if left_token.precedence < op_token.precedence:
                result_strings[0] = "({})".format(result_strings[0])
            elif left_token.precedence == op_token.precedence and \
                    op_token.associativity == TokenAssociativity.RIGHT:
                result_strings[0] = "({})".format(result_strings[0])

        # Right Bracketing
        if right_token.type == TokenType.BINARY_OPERATOR:
            right_token: BinaryOperatorToken
            if right_token.precedence < op_token.precedence:
                result_strings[1] = "({})".format(result_strings[1])
            elif right_token.precedence == op_token.precedence and \
                    (not op_token.commutative) and (op_token.associativity != TokenAssociativity.RIGHT):
                result_strings[1] = "({})".format(result_strings[1])

        return self.eval_function(tuple(result_strings), tuple(result_values))


class UnaryOperatorToken(NonValueToken):
    def __init__(self,
                 name: str,
                 token: str,
                 eval_function: Callable[[str, NumericToken],
                                         Tuple[Tuple[str, ...], Tuple["Token", ...]]]):
        self.arity = 0
        super(UnaryOperatorToken, self).__init__(name,
                                                 token,
                                                 TokenAssociativity.LEFT,
                                                 4,
                                                 TokenType.UNARY_OPERATOR)
        self.eval_function = eval_function

    def eval(self) -> Tuple[Tuple[str, ...], Tuple["Token", ...]]:
        children = self.getChildren()
        if len(children) != 1:
            raise ValueError(f"UnaryOperatorToken: {self} has {len(children)} children, 1 expected")
        child = children[0]
        result_string: str
        result_token: NumericToken

        res_strings, res_tokens = child.eval()
        validateNumericEval(res_strings, res_tokens)
        result_string = res_strings[0]
        # noinspection PyTypeChecker
        result_token = res_tokens[0]
        return self.eval_function(result_string, result_token)


class FunctionToken(NonValueToken):
    def __init__(self,
                 name: str,
                 eval_function: Callable[[Tuple["Token", ...]],
                                         Tuple[Tuple[str, ...], Tuple["Token", ...]]]):
        self.arity = 0
        super(FunctionToken, self).__init__(name,
                                            name,
                                            TokenAssociativity.LEFT,
                                            0,
                                            TokenType.FUNCTION)
        self.eval_function = eval_function

    def eval(self) -> Tuple[Tuple[str, ...], Tuple["Token", ...]]:
        child_nodes = self.getChildren()
        return self.eval_function(tuple(child_nodes))

    def __get_additional_repr__(self) -> str:
        s = super(FunctionToken, self).__get_additional_repr__()
        s += f"arity: {self.arity}"
        return s


class TokenFactory(object):
    def __init__(self):
        pass

    @staticmethod
    def generateToken(token_name: str, value: str) -> Token:
        # Numeric Tokens
        if token_name == "die":
            return DiceToken(
                "die",
                value
            )
        if token_name == "num":
            return NumericToken(
                "num",
                int(value)
            )

        # Binary Operators
        if token_name == "add":
            return BinaryOperatorToken(
                "add",
                "+",
                TokenAssociativity.LEFT,
                2,
                _genBinaryOperatorFunction("+", lambda a, b: a + b),
                True
            )
        if token_name == "subtract":
            return BinaryOperatorToken(
                "subtract",
                "-",
                TokenAssociativity.LEFT,
                2,
                _genBinaryOperatorFunction("-", lambda a, b: a - b),
                False
            )
        if token_name == "multiply":
            return BinaryOperatorToken(
                "multiply",
                "*",
                TokenAssociativity.LEFT,
                3,
                _genBinaryOperatorFunction("*", lambda a, b: a * b),
                True
            )
        if token_name == "divide":
            return BinaryOperatorToken(
                "divide",
                "/",
                TokenAssociativity.LEFT,
                3,
                _genBinaryOperatorFunction("/", lambda a, b: a / b),
                False
            )
        if token_name == "power":
            return BinaryOperatorToken(
                "power",
                "^",
                TokenAssociativity.RIGHT,
                4,
                _genBinaryOperatorFunction("^", lambda a, b: a ** b),
                False
            )

        # Unary Operators
        if token_name == "unary minus":
            return UnaryOperatorToken(
                "unary minus",
                "-",
                _genUnaryOperatorFunction("-", lambda a: -1 * a)
            )

        # Functions
        if token_name == "max":
            return FunctionToken(
                "max",
                _max
            )
        if token_name == "min":
            return FunctionToken(
                "min",
                _min
            )
        if token_name == "rep":
            return FunctionToken(
                "rep",
                _rep
            )

        # Brackets
        if token_name == "left bracket":
            return NonValueToken(
                "left bracket",
                "(",
                TokenAssociativity.LEFT,
                1,
                TokenType.LEFT_BRACKET
            )
        if token_name == "right bracket":
            return NonValueToken(
                "right bracket",
                ")",
                TokenAssociativity.LEFT,
                1,
                TokenType.RIGHT_BRACKET
            )

        # Comma
        if token_name == "comma":
            return NonValueToken(
                "comma",
                ",",
                TokenAssociativity.LEFT,
                1,
                TokenType.COMMA
            )


def _genBinaryOperatorFunction(
        token: str,
        binaryOperatorFunction: Callable[[float, float], float]) -> \
        Callable[[Tuple[str, ...], Tuple["NumericToken", ...]],
                 Tuple[Tuple[str, ...], Tuple["Token", ...]]]:
    def binaryNodeOperatorFunction(result_strings: Tuple[str, ...], result_nodes: Tuple["NumericToken", ...]) \
            -> Tuple[Tuple[str, ...], Tuple["Token", ...]]:
        if len(result_nodes) != 2:
            raise ValueError(f"result_nodes has {len(result_nodes)} parameters, 2 expected")
        if len(result_strings) != 2:
            raise ValueError(f"result_nodes has {len(result_strings)} parameters, 2 expected")

        left_token: NumericToken = result_nodes[0]
        right_token: NumericToken = result_nodes[1]

        result_value = binaryOperatorFunction(left_token.value, right_token.value)
        result_string = "{}{}{}".format(result_strings[0], token, result_strings[1])
        return (result_string, ), (NumericToken("num", result_value),)

    return binaryNodeOperatorFunction


def _genUnaryOperatorFunction(
        token: str,
        unaryOperatorFunction: Callable[[float], float]) -> \
        Callable[[str, NumericToken],
                 Tuple[Tuple[str, ...], Tuple["Token", ...]]]:
    def unaryNodeOperatorFunction(result_string: str, result_node: NumericToken) \
            -> Tuple[Tuple[str, ...], Tuple["Token", ...]]:

        result_value = unaryOperatorFunction(result_node.value)
        new_result_string = "{}{}".format(token, result_string)
        return (new_result_string, ), (NumericToken("num", result_value),)

    return unaryNodeOperatorFunction


def validateNumericEval(res_strings: Tuple[str, ...], res_tokens: Tuple["Token", ...]):
    assert len(res_strings) == 1
    assert len(res_tokens) == 1
    assert isinstance(res_tokens[0], NumericToken)


def validateNumericEvalList(res_strings: Tuple[str, ...], res_tokens: Tuple["Token", ...]):
    assert len(res_strings) == 1
    for token in res_tokens:
        assert isinstance(token, NumericToken)


def _rep(children: Tuple["Token", ...]) -> Tuple[Tuple[str, ...], Tuple["Token", ...]]:
    if len(children) != 2:
        raise Exception(f"Function rep expects 2 parameters, received {len(children)}")

    function_child = children[0]
    repeat_child = children[1]

    rep_strings, rep_tokens = repeat_child.eval()
    validateNumericEval(rep_strings, rep_tokens)
    # noinspection PyTypeChecker
    rep_token: "NumericToken" = rep_tokens[0]
    result_strings = []
    result_tokens = []
    # TODO check if rep_token.value is an int
    for _ in range(int(rep_token.value)):
        res_strings, res_tokens = function_child.eval()
        validateNumericEval(res_strings, res_tokens)
        result_strings += res_strings
        result_tokens += res_tokens

    out_string = "[" + ", ".join(result_strings) + "]"
    out_tokens = result_tokens
    return (out_string, ), tuple(out_tokens)


def _max(children: Tuple["Token", ...]) -> Tuple[Tuple[str, ...], Tuple["Token", ...]]:
    child_strings = []
    child_tokens: List[NumericToken] = []

    for child in children:
        res_strings, res_tokens = child.eval()
        validateNumericEvalList(res_strings, res_tokens)
        child_strings += res_strings
        child_tokens += res_tokens

    out_string = ", ".join(child_strings)
    out_string = "max(" + out_string + ")"
    out_value = max([token.value for token in child_tokens])
    return (out_string, ), (NumericToken("num", out_value), )


def _min(children: Tuple["Token", ...]) -> Tuple[Tuple[str, ...], Tuple["Token", ...]]:
    child_strings = []
    child_tokens: List[NumericToken] = []

    for child in children:
        res_strings, res_tokens = child.eval()
        validateNumericEvalList(res_strings, res_tokens)
        child_strings += res_strings
        child_tokens += res_tokens

    out_string = ", ".join(child_strings)
    out_string = "min(" + out_string + ")"
    out_value = min([token.value for token in child_tokens])
    return (out_string, ), (NumericToken("num", out_value), )
