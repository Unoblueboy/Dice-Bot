# from TokenParser import Node
from typing import List


def _genBinaryOperationEvalFunction(token_string, op_string):
    def evalFunction(res_strings: List[str], res_values: List[float]):
        out_string = res_strings[0] + token_string + res_strings[1]
        out_val_str = "{}{}{}".format(res_values[0], op_string, res_values[1])
        out_values = eval(out_val_str)
        return out_string, out_values
    return evalFunction


def _unitaryMinus(res_strings: List[str], res_values: List[float]):
    out_string = "-" + res_strings[0]
    out_value = -1*res_values[0]
    return out_string, out_value


# Non node-callable Functions
def _max(res_strings: List[str], res_values: List[float]) -> (str, float):
    out_string = ", ".join(res_strings)
    out_string = "max(" + out_string + ")"
    out_value = max(res_values)

    return out_string, out_value


# Node-callable functions
def _rep(children) -> (str, List[float]):
    rep_str, rep_val = children[1].eval()
    result_strings = []
    result_values = []
    for _ in range(rep_val):
        res_string, res_value = children[0].eval()
        result_strings.append(res_string)
        result_values.append(res_value)

    out_string = "{" + ", ".join(result_strings) + "}"
    out_values = result_values
    return out_string, out_values
