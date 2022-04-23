from typing import Dict, List

import Parser.Mappings as Mappings
from Nodes.Token import TokenFactory, TokenType, Token


def find_matching_tokens(remaining_string) -> Dict:
    matching_tokens_data = {}
    for token_name, regex in Mappings.RegexTokenMapping.items():
        matches = regex.match(remaining_string)
        if not matches:
            continue

        value, end = matches.group(1, matches.lastindex)
        matching_tokens_data[token_name] = {
            "value": value,
            "remaining string": end
        }

    if len(matching_tokens_data) == 0:
        raise Exception("Unknown token")

    return matching_tokens_data


def handle_clash(matching_tokens_data: Dict, prev_token: Token):
    token_names = set(matching_tokens_data.keys())
    if token_names == {"unary minus", "subtract"}:
        if (prev_token is None) or prev_token.type in [TokenType.COMMA,
                                                       TokenType.LEFT_BRACKET,
                                                       TokenType.BINARY_OPERATOR]:
            return {"unary minus": matching_tokens_data["unary minus"]}
        else:
            return {"subtract": matching_tokens_data["subtract"]}
    if token_names == {"die", "num"}:
        return {"die": matching_tokens_data["die"]}
    raise NotImplementedError()


def get_tokens(input_str) -> List[Token]:
    input_str = input_str.replace(" ", "")
    tokens = []

    remaining_string = input_str
    prev_token = None
    while len(remaining_string) > 0:
        # find matching tokens
        matching_tokens_data = find_matching_tokens(remaining_string)

        # deal with possible clashes
        if len(matching_tokens_data) != 1:
            matching_token_data = handle_clash(matching_tokens_data, prev_token)
        else:
            matching_token_data = matching_tokens_data

        # extract token data
        matching_token_name, matching_token_dict_value = matching_token_data.popitem()
        matching_token_value = matching_token_dict_value["value"]

        token = TokenFactory.generateToken(matching_token_name, matching_token_value)

        # add token to token list and cut down remaining string
        tokens.append(token)
        prev_token = token
        remaining_string = matching_token_dict_value["remaining string"]

    return tokens


if __name__ == '__main__':
    print(get_tokens("5d6 + 1"))
    print()
    print(get_tokens("-5d6 - 1 + -2"))
    print()
    print(get_tokens("max(d6, 12, d8)"))
