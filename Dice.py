# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 23:31:54 2019

@author: Nathan Douglas
"""

from random import randint, shuffle
from collections import OrderedDict, deque
import re


class Dice(object):
    def __init__(self, dice_string):
        self.dice_string = dice_string
        if dice_string[0] == "-":
            self.dice_string = self.dice_string[1:]
        self._process_dice_tokens()

    def _process_dice_tokens(self):
        # Get dice from dice_string
        dice_regex = re.compile(r"^([0-9]*)(d[0-9]+)(.*)", re.IGNORECASE)
        num, sides, end = dice_regex.match(self.dice_string).group(1, 2, 3)
        if num == "":
            num = "1"
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
        values = self._generate_base_dice_pool()
        if len(self.operations) == 0 or self.operations[0] == "!":
            token_str_tokens = [str(val) for val in values]
        else:
            output = self._generate_operation_dice_pool_and_string_tokens(values)
            values, token_str_tokens = output

        token_str = Dice._generate_token_string(token_str_tokens)
        return values, token_str

    def _generate_base_dice_pool(self):
        values = []
        for _ in range(self.num):
            new_roll = randint(1, self.sides)
            values.append(new_roll)

        if len(self.operations) > 0 and self.operations[0] == "!":
            values = self._generate_exploding_dice(values)
        return values

    def _generate_exploding_dice(self, values):
        # Error out if try to explode die with 1 or less sides
        if self.sides <= 1:
            raise Exception("Can't Explode 1 or less sided die")
        # Explode the dice
        additional_values = []
        additional_rolls = sum([1 for val in values if val == self.sides])
        while additional_rolls != 0:
            new_roll = randint(1, self.sides)
            additional_values.append(new_roll)
            if new_roll < self.sides:
                additional_rolls -= 1

        values += additional_values

        return values

    def _generate_operation_dice_pool(self, sorted_values):
        # sorted_values = sorted(values)
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
        if len(values) == 0:
            values = [0]
        return values, start_index, end_index

    @staticmethod
    def _generate_operation_string_tokens(sorted_values,
                                          start_index,
                                          end_index):
        str_tokens = []
        for i in range(len(sorted_values)):
            val = sorted_values[i]
            if i < start_index or i >= end_index:
                str_tokens.append("~~{}~~".format(val))
            else:
                str_tokens.append(str(val))
        shuffle(str_tokens)
        return str_tokens

    def _generate_operation_dice_pool_and_string_tokens(self, values):
        sorted_values = sorted(values)
        values, start_index, end_index = self._generate_operation_dice_pool(
                                                                sorted_values)
        str_tokens = Dice._generate_operation_string_tokens(sorted_values,
                                                            start_index,
                                                            end_index)
        return values, str_tokens

    @staticmethod
    def _generate_token_string(str_tokens):
        return "(" + "+".join(str_tokens) + ")"


if __name__ == '__main__':
    x = Dice("6d6!")
    print(x.roll())
    x = Dice("32d25")
    print(x.roll())
    x = Dice("5d6kh3dh1")
    print(x.roll())
    x = Dice("2d6kh1")
    print(x.roll())

    # t = TokenList()
    # t.printTokens()

    # from pprint import pprint
    # from TokenParser import get_tokens, shunting_yard
    #
    # print()
    # pprint([str(x) for x in get_tokens("1+2+3")])
    # print()
    # pprint([str(x) for x in get_tokens("1+2+3d6")])
    # print()
    # pprint([str(x) for x in get_tokens("-2d6+-2d6-2d6")])
    # print()
    # pprint([str(x) for x in get_tokens("-2d6+-2d6-2d6")])
    # print()
    # pprint([str(x) for x in get_tokens("max(1, 2)")])
    # print()
    # print([str(x) for x in get_tokens("max(-2d6+-2d6-2d6, 1+2+3d6, 23, 5 + 4)")])
    # print()
    # # pprint(test_get_tokens("-2d6+-2d6-2d6"))
    #
    # print([str(x) for x in shunting_yard(get_tokens("-2d6+-2d6-2d6"))])
    # print()
    # print([str(x) for x in shunting_yard(get_tokens("max(1, 2)"))])
    # print()
    # print([str(x) for x in shunting_yard(get_tokens("max(-2d6+-2d6-2d6, 1+2+3d6, 23, 5 + 4)"))])
    # print()
    # print(shunting_yard(get_tokens("max(-2d6+-2d6-2d6, 1+2+3d6, 23, max(5 + 4, 22d6))")))
    # print()
    # pprint(test_shunting_yard(test_get_tokens("-2d6+-2d6-2d6")))
