from enum import Enum
class cell:
    def __init__(self, m, n):
        self.m = m
        self.n = n
        self.type_cell = Type.empty

class Type(Enum):
    empty = 0 
    snake = 1
    apple = 2
    
