from enum import Enum
from Dice import Dice
from typing import Callable
from Functions import _max, _genBinaryOperationEvalFunction, _unitaryMinus, _rep
import re


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
    def __init__(self,
                 name: str,
                 regex_str: str,
                 token_type: TokenType):
        self.name = name
        self.regex_str = regex_str
        self.regex = re.compile(self.regex_str, re.IGNORECASE)
        self.type = token_type

    def __repr__(self):
        s = """
name:               {},
    regex string:   {},
    type:           {}""".format(self.name, self.regex_str, self.type.name)

        return s


class NumericToken(Token):
    def __init__(self,
                 name: str,
                 regex_str: str):
        super(NumericToken, self).__init__(name, regex_str, TokenType.NUMERIC)
        self.value = None

    def copyWithValue(self, value: str):
        token = self.__class__(self.name, self.regex_str)
        token.value = value
        return token

    def eval(self, result_strings="", result_values=0):
        return self.value, int(self.value)

    def __repr__(self):
        s = super(NumericToken, self).__repr__()
        s += """
    value:          {}""".format(self.value)

        return s

    def __str__(self):
        if self.value is None:
            return "None"
        return self.value


class DiceToken(NumericToken):
    def __init__(self,
                 name: str,
                 regex_str: str):
        super(DiceToken, self).__init__(name, regex_str)
        self.type = TokenType.DICE
        self.value = None
        self.dice = None

    def eval(self, result_strings="", result_values=0):
        self.dice = Dice(self.value)
        values, token_str = self.dice.roll()
        return token_str, sum(values)


class NonNumericToken(Token):
    def __init__(self,
                 name: str,
                 regex_str: str,
                 token: str,
                 associativity: TokenAssociativity,
                 precedence: int,
                 token_type: TokenType,
                 eval_function: Callable):
        super(NonNumericToken, self).__init__(name, regex_str, token_type)
        self.token = token
        self.associativity = associativity
        self.precedence = precedence
        self.eval = eval_function

    def __repr__(self):
        s = super(NonNumericToken, self).__repr__()
        s += """
    token:          {}
    associativity:  {},
    precedence:     {}""".format(self.token,
                                 self.associativity.name,
                                 self.precedence)

        return s

    def __str__(self):
        return self.token


class FunctionToken(NonNumericToken):
    def __init__(self, name: str, eval_function: Callable, node_callable=False):
        self.arity = 0
        regex_str = r"({})(.*)".format(name)
        super(FunctionToken, self).__init__(name,
                                            regex_str,
                                            name,
                                            TokenAssociativity.LEFT,
                                            0,
                                            TokenType.FUNCTION,
                                            eval_function)
        self.node_callable = node_callable

    def __repr__(self):
        s = super(FunctionToken, self).__repr__()
        s += """
    arity:          {}""".format(self.arity)
        return s

    def copyWithArity(self, arity):
        new_token = FunctionToken(self.name, self.eval, self.node_callable)
        new_token.arity = arity
        return new_token


class TokenList(object):
    def __init__(self):
        self.tokens = []
        self.initTokens()

    def initTokens(self):
        # Numeric Tokens
        self.addDiceToken("die", r"^(([0-9]*)(d[0-9]+)(!|((kh|kl|dh|dl)[0-9]+)*))(.*)")
        self.addNumericToken("num", r"^([0-9]+)(.*)")

        # Binary Operators
        self.addBinaryOperatorToken("add",
                                    "+",
                                    TokenAssociativity.LEFT,
                                    2,
                                    _genBinaryOperationEvalFunction("+", "+"))
        self.addBinaryOperatorToken("subtract",
                                    "-",
                                    TokenAssociativity.LEFT,
                                    2,
                                    _genBinaryOperationEvalFunction("-", "-"))
        self.addBinaryOperatorToken("multiply",
                                    "*",
                                    TokenAssociativity.LEFT,
                                    3,
                                    _genBinaryOperationEvalFunction("*", "*"))
        self.addBinaryOperatorToken("divide",
                                    "/",
                                    TokenAssociativity.LEFT,
                                    3,
                                    _genBinaryOperationEvalFunction("/", "/"))
        self.addBinaryOperatorToken("power",
                                    "^",
                                    TokenAssociativity.RIGHT,
                                    4,
                                    _genBinaryOperationEvalFunction("^", "**"))

        # Unary operators
        self.addUnaryOperatorToken("Unary Minus",
                                   "-", _unitaryMinus)

        # functions
        self.addFunctionToken("max", _max)
        self.addFunctionToken("rep", _rep, node_callable=True)

        # Brackets
        self.addBracketToken("left bracket", "(", TokenType.LEFT_BRACKET)
        self.addBracketToken("right bracket", ")", TokenType.RIGHT_BRACKET)

        # Comma
        self.addCommaToken()

    def addNumericToken(self, name: str, regex_str: str):
        token = NumericToken(name, regex_str)
        self.tokens.append(token)

    def addDiceToken(self, name: str, regex_str: str):
        token = DiceToken(name, regex_str)
        self.tokens.append(token)

    def addBinaryOperatorToken(self,
                               name: str,
                               token: str,
                               associativity: TokenAssociativity,
                               precedence: int,
                               eval_function: Callable):
        regex = r"^(\{})(.*)".format(token)
        token = NonNumericToken(name, regex, token, associativity, precedence, TokenType.BINARY_OPERATOR, eval_function)
        self.tokens.append(token)

    def addUnaryOperatorToken(self,
                              name: str,
                              token: str,
                              eval_function: Callable):
        regex = r"^(\{})(.*)".format(token)
        token = NonNumericToken(name, regex, token, TokenAssociativity.LEFT, 4, TokenType.UNARY_OPERATOR, eval_function)
        self.tokens.append(token)

    def addBracketToken(self,
                        name: str,
                        token: str,
                        token_type: TokenType):
        regex = r"^(\{})(.*)".format(token)
        token = NonNumericToken(name, regex, token, TokenAssociativity.LEFT, 1, token_type, lambda: None)
        self.tokens.append(token)

    def addCommaToken(self):
        token = NonNumericToken("comma", r"^(\,)(.*)", ",", TokenAssociativity.LEFT, 1, TokenType.COMMA, lambda: None)
        self.tokens.append(token)

    def addFunctionToken(self,
                         name: str,
                         eval_function: Callable,
                         node_callable=False):
        token = FunctionToken(name, eval_function, node_callable)
        self.tokens.append(token)

    def getTokenFromName(self,
                         name: str):
        for token in self.tokens:
            if token.name == name:
                return token

        raise Exception("No Token of Name {}".format(name))

    def printTokens(self):
        for token in self.tokens:
            print(token)


