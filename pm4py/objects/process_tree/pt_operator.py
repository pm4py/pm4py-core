from enum import Enum
import warnings

warnings.warn("the pt_operator.Operator class has been deprecated. Please use process_tree.Operator instead!")

from pm4py.objects.process_tree.obj import Operator
