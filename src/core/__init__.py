"""
Core classes for the linear programming solver.
"""

from .problem import LinearProblem
from .solution import (
    Solution,
    ProgressPoint,
    NumericalQuality,
    SolutionTable,
    to_solution_table,
)
from .constraint import LinearConstraint
from .bound import VariableBound
from .constants import (
    FEASIBILITY_TOLERANCE,
    OPTIMALITY_TOLERANCE,
    BOUND_TOLERANCE,
    PARSING_TOLERANCE,
    DEFAULT_INFINITY,
)
from .verification import verify_solution, compare_solutions
from .exceptions import (
    LPError,
    LPParseError,
    LPInfeasibleError,
    LPUnboundedError,
    LPUnsolvedError,
    LPVisualizationError,
    LPConfigurationError,
)

__all__ = [
    "LinearProblem",
    "Solution",
    "ProgressPoint",
    "NumericalQuality",
    "SolutionTable",
    "to_solution_table",
    "LinearConstraint",
    "VariableBound",
    "FEASIBILITY_TOLERANCE",
    "OPTIMALITY_TOLERANCE",
    "BOUND_TOLERANCE",
    "PARSING_TOLERANCE",
    "DEFAULT_INFINITY",
    "verify_solution",
    "compare_solutions",
    "LPError",
    "LPParseError",
    "LPInfeasibleError",
    "LPUnboundedError",
    "LPUnsolvedError",
    "LPVisualizationError",
    "LPConfigurationError",
]