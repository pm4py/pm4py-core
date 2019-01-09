from enum import Enum


class Operator2(Enum):
    SEQUENCE = '->'
    XOR = 'X'
    PARALLEL = '+'
    LOOP = '*'

    '''
    SEQUENCE = u'\u2192'
    XOR = u'\u00d7'
    PARALLEL = u'\u002b'
    LOOP = u'\u27f2'
    '''
    def __str__(self):
        return self.value
