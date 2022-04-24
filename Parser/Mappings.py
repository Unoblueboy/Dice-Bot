import re
from typing import Dict, Pattern

RegexTokenMapping: Dict[str, Pattern] = {
    "die": re.compile(r"^(([0-9]*)(d[0-9]+)(!|((kh|kl|dh|dl)[0-9]+)*))(.*)", re.IGNORECASE),
    "num": re.compile(r"^([0-9]+)(.*)", re.IGNORECASE),
    "add": re.compile(r"^(\+)(.*)", re.IGNORECASE),
    "subtract": re.compile(r"^(-)(.*)", re.IGNORECASE),
    "multiply": re.compile(r"^(\*)(.*)", re.IGNORECASE),
    "divide": re.compile(r"^(/)(.*)", re.IGNORECASE),
    "power": re.compile(r"^(\^)(.*)", re.IGNORECASE),
    "unary minus": re.compile(r"^(-)(.*)", re.IGNORECASE),
    "max": re.compile(r"^(max)(.*)", re.IGNORECASE),
    "min": re.compile(r"^(min)(.*)", re.IGNORECASE),
    "rep": re.compile(r"^(rep)(.*)", re.IGNORECASE),
    "left bracket": re.compile(r"^(\()(.*)", re.IGNORECASE),
    "right bracket": re.compile(r"^(\))(.*)", re.IGNORECASE),
    "comma": re.compile(r"^(,)(.*)", re.IGNORECASE)
}
