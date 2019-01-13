from enum import Enum


class Operator(Enum):
    # sequence operator
    SEQUENCE = '->'
    # exclusive choice operator
    XOR = 'X'
    # parallel operator
    PARALLEL = '+'
    # loop operator
    LOOP = '*'

    '''
    SEQUENCE = u'\u2192'
    XOR = u'\u00d7'
    PARALLEL = u'\u002b'
    LOOP = u'\u27f2'
    '''
    def __str__(self):
        return self.value
