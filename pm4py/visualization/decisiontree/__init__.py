from pm4py.visualization.decisiontree import variants, visualizer

from pm4py.util import constants
import warnings

if constants.SHOW_INTERNAL_WARNINGS:
    warnings.warn("The decisiontree visualizer will be removed in a future release (use Scikit Learn instead).")
