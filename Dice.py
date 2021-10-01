# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 23:31:54 2019

@author: Natha
"""

from random import randint, shuffle
import re
from collections import OrderedDict, deque


class Dice(object):
    def __init__(self, dice_string):
        self.dice_string = dice_string
        if dice_string[0] == "-":
            self.dice_string = self.dice_string[1:]
        self.processDiceTokens()
        # print(self.num)
        # print(self.sides)
        # print(self.operations)

    def processDiceTokens(self):
        # Get dice from dice_string
        dice_regex = re.compile(r"^([0-9]*)(d[0-9]+)(.*)", re.IGNORECASE)
        num, sides, end = dice_regex.match(self.dice_string).group(1, 2, 3)
        self.num = int(num)
        self.sides = int(sides[1:])

        # Get the additional operations to perform on the dice
        self.operations = []
        op_string = end
        if op_string == "!":
            self.operations = ["!"]
            return
        # If the dice explodes, that should be the only operation, else
        # find all the operations, these are of the form
        # kh[0-9]+, kl[0-9]+, dh[0-9]+, kl[0-9]+
        op_regex = re.compile("(kh|kl|dh|dl)([0-9]+)(.*)", re.IGNORECASE)
        while len(op_string) != 0:
            op, num, end = op_regex.match(op_string).group(1, 2, 3)
            self.operations.append((op, int(num)))
            op_string = end


    def roll(self):
        values = []
        i = 0
        while i < self.num:
            values.append(randint(1, self.sides))
            i += 1
        if len(self.operations) == 0:
            # No operations so simply construct token string
            token_str = "(" + "+".join([str(x) for x in values]) + ")"
            return values, token_str
        elif self.operations[0] == "!":
            # Explode the dice
            additional_rolls = sum([1 for val in values if val == self.sides]) # number of dice with max roll
            while additional_rolls != 0:
                new_roll = randint(1, self.sides)
                values.append(new_roll)
                if new_roll < self.sides:
                    additional_rolls -= 1

            #create token string
            token_str = "(" + "+".join([str(x) for x in values]) + ")"
            return values, token_str
        else:
            sorted_values = sorted(values)
            start_index = 0
            end_index = len(sorted_values)
            for op, num in self.operations:
                if op == "kh":
                    start_index = max(start_index, end_index - num)
                elif op == "kl":
                    end_index = min(end_index, start_index + num)
                elif op == "dh":
                    end_index = end_index - num
                elif op == "dl":
                    start_index = start_index + num


            values = sorted_values[start_index:end_index]

            token_str_tokens = []
            for i in range(len(sorted_values)):
                val = sorted_values[i]
                if i < start_index or i >= end_index:
                    token_str_tokens.append("~~{}~~".format(val))
                else:
                    token_str_tokens.append(str(val))
            shuffle(token_str_tokens)

            token_str = "(" + "+".join(token_str_tokens) + ")"

            if len(values) == 0:
                return [0], token_str
            return values, token_str



class Roll(object):
    token_regexes = OrderedDict(
            [("die", re.compile(r"^(-?)([0-9]*)(d[0-9]+)((kh|kl|dh|dl)[0-9]+)*(.*)", re.IGNORECASE)),
             ("num", re.compile(r"^(-?[0-9]+)(.*)", re.IGNORECASE)),
             ("add", re.compile(r"^(\+)(.*)", re.IGNORECASE)),
             ("sub", re.compile(r"^(\-)(.*)", re.IGNORECASE)),
             ("mul", re.compile(r"^(\*)(.*)", re.IGNORECASE)),
             ("div", re.compile(r"^(\/)(.*)", re.IGNORECASE)),
             ("exp", re.compile(r"^(\^)(.*)", re.IGNORECASE)),
             ("lbr", re.compile(r"^(\()(.*)", re.IGNORECASE)), # left bracket
             ("rbr", re.compile(r"^(\))(.*)", re.IGNORECASE))])# right bracket
    numeric_token = ["die", "num"]
    operator_token = ["add", "sub", "mul", "div", "exp"]
    operator_associativty = {
            "add": "L",
            "sub": "L",
            "mul": "L",
            "div": "L",
            "exp": "R",
            "lbr": "L",
            "rbr": "L", }
    operator_name = {
            "+": "add",
            "-": "sub",
            "*": "mul",
            "/": "div",
            "^": "exp",
            "(": "lbr",
            ")": "rbr"}
    operator_precedence = {
            "lbr": 1,
            "rbr": 1,
            "add": 2,
            "sub": 2,
            "mul": 3,
            "div": 3,
            "exp": 4}
    # Left associative implies a~b~c = (a~b)~c
    # Right associative implies a~b~c = a~(b~c)
    function_token = []
    brackets = ["lbr", "rbr"]

    def __init__(self, input_str):
        input_str = input_str.replace(" ", "")
        self.input_str = input_str
        self.out_str, self.roll_tokens = self.get_tokens(input_str)
        self.rpn = self.shunting_yard(self.roll_tokens)
        self.final_result = self.parse_rpn(self.rpn)

    def get_tokens(self, input_str):
        out_str = ""
        tokens = []
        prev_token = ""
        while len(input_str) != 0:
            if input_str[0] == '-':
                end = input_str[1:]

                if Roll.is_in_category(prev_token, ["rbr", "die", "num"]) and\
                   Roll.is_in_category(end, ["lbr", "die", "num"]):
                    tokens.append("-")
                    input_str = end
                    out_str += "-"

                    prev_token = "-"
                    continue
            for token_type, reg in self.token_regexes.items():
                matches = reg.match(input_str)
                if matches and token_type != "die":
                    token, end = matches.group(1, 2)
                    tokens.append(token)
                    input_str = end
                    out_str += token

                    prev_token = token
                    break
                elif matches and token_type == "die":
                    sign, dice_string, end = matches.group(2, 1, 8)
                    input_str = end

                    # if not num:
                    #     num = "1"
                    # num = int(num)
                    # val = int(val[1:])
                    # values = Dice(num, val).roll()
                    # token_str = "(" + "+".join([str(x) for x in values]) + ")"

                    dice = Dice(dice_string)
                    values, token_str = dice.roll()

                    if sign:
                        token_str = "-" + token_str
                        tokens.append("-1")
                        tokens.append("*")

                    tokens.append("(")
                    for v in values:
                        tokens.append(str(v))
                        tokens.append("+")
                    tokens.pop()
                    tokens.append(")")

                    out_str += token_str
                    prev_token = ")"
                    break
            else:
                raise Exception("STOP!!! YOU HAVE DONE SOMETHING ILLEGAL")
        return out_str, tokens

    def shunting_yard(self, tokens):
        input_tokens = deque(tokens)
        output_queue = deque()
        operator_stack = deque()
        while len(input_tokens) > 0:
            token = input_tokens.popleft()

            number = Roll.is_in_category(token, self.numeric_token)
            if number:
                output_queue.append(token)
                continue

            function = Roll.is_in_category(token, self.function_token)
            if function:
                operator_stack.append(token)
                continue

            operator = Roll.is_in_category(token, self.operator_token)
            if operator:
                operator = token
                if len(operator_stack) != 0:
                    op_name = Roll.operator_name[operator]
                    top_name = Roll.operator_name[operator_stack[-1]]
                    condition1 = top_name in self.function_token
                    condition2 = top_name in self.operator_token
                    condition3 = Roll.operator_precedence[top_name] >\
                        Roll.operator_precedence[op_name]
                    condition4 = Roll.operator_precedence[top_name] ==\
                        Roll.operator_precedence[op_name]
                    condition5 = Roll.operator_associativty[top_name] == "L"
                    condition6 = not Roll.is_in_category(
                        operator_stack[-1], ["lbr"])
                while len(operator_stack) != 0 and condition6 and\
                    ((condition1) or ((condition2)
                                      and ((condition3)
                                           or ((condition4)
                                               and (condition5))))):
                    output_queue.append(operator_stack.pop())
                    if len(operator_stack) != 0:
                        op_name = Roll.operator_name[operator]
                        top_name = Roll.operator_name[operator_stack[-1]]
                        condition1 = top_name in self.function_token
                        condition2 = top_name in self.operator_token
                        condition3 = Roll.operator_precedence[top_name] >\
                            Roll.operator_precedence[op_name]
                        condition4 = Roll.operator_precedence[top_name] ==\
                            Roll.operator_precedence[op_name]
                        condition5 = Roll.operator_associativty[top_name] ==\
                            "L"
                        condition6 = not Roll.is_in_category(
                            operator_stack[-1], ["lbr"])
                operator_stack.append(token)
                continue

            l_bracket = Roll.is_in_category(token, ["lbr"])
            if l_bracket:
                operator_stack.append(token)
                continue

            r_bracket = Roll.is_in_category(token, ["rbr"])
            if r_bracket:
                try:
                    while not Roll.is_in_category(operator_stack[-1], ["lbr"]):
                        output_queue.append(operator_stack.pop())
                    # now we ya yeet the l bracket and forget about it
                    operator_stack.pop()
                except IndexError:
                    raise Exception("Stop!! you have too many right brackets")
                continue

        while len(operator_stack) != 0:
            if Roll.is_in_category(operator_stack[-1], ["lbr"]):
                raise Exception("Stop!! you have too many left brackets")
            output_queue.append(operator_stack.pop())

        return output_queue

    def parse_rpn(self, rpn):
        result_stack = []
        for token in rpn:
            if Roll.is_in_category(token, ["num"]):
                result_stack.append(float(token))
                continue
            else:  # token is some kind of operator
                if Roll.is_in_category(token, self.function_token):
                    continue
                elif Roll.is_in_category(token, self.operator_token):
                    if token == "+":
                        val1 = result_stack.pop()
                        val2 = result_stack.pop()
                        result_stack.append(val2+val1)
                    elif token == "-":
                        val1 = result_stack.pop()
                        val2 = result_stack.pop()
                        result_stack.append(val2-val1)
                    elif token == "*":
                        val1 = result_stack.pop()
                        val2 = result_stack.pop()
                        result_stack.append(val2*val1)
                    elif token == "/":
                        val1 = result_stack.pop()
                        val2 = result_stack.pop()
                        result_stack.append(val2/val1)
                    elif token == "^":
                        val1 = result_stack.pop()
                        val2 = result_stack.pop()
                        result_stack.append(val2**val1)
                    else:
                        raise Exception("This is an illegal operation")
                    continue
        if len(result_stack) != 1:
            raise Exception("AN ERROR HAS OCCURRED, FIX IT BISCH")
        else:
            result = result_stack[0]
            if result % 1 == 0:
                result = int(result)
            return result

    def is_in_category(token, category):
        for token_type in category:
            match = Roll.token_regexes[token_type].match(token)
            if match:
                return match
        else:
            return None


if __name__ == '__main__':
    x = Dice("6d6!")
    print(x.roll())
    x = Dice("32d25")
    print(x.roll())
    x = Dice("5d6kh3dh1")
    print(x.roll())
    # x1 = Roll("-2d6-2d6-2d6")
