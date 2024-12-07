from enum import Enum


class MatchyComparer(Enum):
    gt = "gt"
    gte = "gte"
    lt = "lt"
    lte = "lte"
    e = "e"
    _in = "in"
