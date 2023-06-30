from pm4py.algo.querying.llm.abstractions import *
from pm4py.algo.querying.llm.connectors import openai as perform_query

import warnings
warnings.warn("the pm4py.algo.querying.openai package is deprecated. Please use pm4py.algo.querying.llm.abstractions instead.")
