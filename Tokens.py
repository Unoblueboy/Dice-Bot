from enum import Enum
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

    def evalDice(self):
        # TODO: evaluate dice in DiceToken
        pass


class NonNumericToken(Token):
    def __init__(self,
                 name: str,
                 regex_str: str,
                 token: str,
                 associativity: TokenAssociativity,
                 precedence: int,
                 token_type: TokenType):
        self.token = token
        self.associativity = associativity
        self.precedence = precedence
        super(NonNumericToken, self).__init__(name, regex_str, token_type)

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
    def __init__(self, name: str):
        self.arity = 0
        regex_str = r"({})(.*)".format(name)
        super(FunctionToken, self).__init__(name, regex_str, name, TokenAssociativity.LEFT, 0, TokenType.FUNCTION)

    def __repr__(self):
        s = super(FunctionToken, self).__repr__()
        s += """
    arity:          {}""".format(self.arity)
        return s

    def copyWithArity(self, arity):
        new_token = FunctionToken(self.name)
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
                                    2)
        self.addBinaryOperatorToken("subtract",
                                    "-",
                                    TokenAssociativity.LEFT,
                                    2)
        self.addBinaryOperatorToken("multiply",
                                    "*",
                                    TokenAssociativity.LEFT,
                                    3)
        self.addBinaryOperatorToken("divide",
                                    "/",
                                    TokenAssociativity.LEFT,
                                    3)
        self.addBinaryOperatorToken("power",
                                    "^",
                                    TokenAssociativity.RIGHT,
                                    4)

        # Unary operators
        # TODO: Properly handle unary minus
        self.addUnaryOperatorToken("Unary Minus",
                                   "-")

        # functions
        # TODO: Implement a dedicated function token class
        self.addFunctionToken("max")

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
                               precedence: int):
        regex = r"^(\{})(.*)".format(token)
        token = NonNumericToken(name, regex, token, associativity, precedence, TokenType.BINARY_OPERATOR)
        self.tokens.append(token)

    def addUnaryOperatorToken(self,
                              name: str,
                              token: str):
        regex = r"^(\{})(.*)".format(token)
        token = NonNumericToken(name, regex, token, TokenAssociativity.LEFT, 4, TokenType.UNARY_OPERATOR)
        self.tokens.append(token)

    def addBracketToken(self, name, token, token_type):
        regex = r"^(\{})(.*)".format(token)
        token = NonNumericToken(name, regex, token, TokenAssociativity.LEFT, 1, token_type)
        self.tokens.append(token)

    def addCommaToken(self):
        token = NonNumericToken("comma", r"^(\,)(.*)", ",", TokenAssociativity.LEFT, 1, TokenType.COMMA)
        self.tokens.append(token)

    def addFunctionToken(self, name):
        token = FunctionToken(name)
        self.tokens.append(token)

    def getTokenFromName(self, name: str):
        for token in self.tokens:
            if token.name == name:
                return token

        raise Exception("No Token of Name {}".format(name))

    def printTokens(self):
        for token in self.tokens:
            print(token)
