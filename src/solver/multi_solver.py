"""
Multiple linear programming problem solver.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import time

from ..core import LinearProblem, Solution
from ..parser import MultiLPParser
from ..matrix import LPBuilder
from .gurobi import GurobiSolver as SolverLP
from .gurobi import GurobiSolver


@dataclass
class ProblemResult:
    """Result of solving an individual problem."""
    problem: LinearProblem
    solution: Solution
    parse_time: float = 0.0
    build_time: float = 0.0
    solve_time: float = 0.0
    total_time: float = 0.0
    error: Optional[str] = None


@dataclass
class MultiSolverResult:
    """Result of solving multiple problems."""
    results: List[ProblemResult] = field(default_factory=list)
    total_parse_time: float = 0.0
    total_build_time: float = 0.0
    total_solve_time: float = 0.0
    total_time: float = 0.0
    verbose: bool = False
    solver_name: str = "unknown"  # Track which solver was used

    def get_successful_results(self) -> List[ProblemResult]:
        """Return only successful results."""
        return [r for r in self.results if r.error is None]

    def get_failed_results(self) -> List[ProblemResult]:
        """Return only failed results."""
        return [r for r in self.results if r.error is not None]


class MultiSolver:
    """Solver for multiple linear programming problems."""

    def __init__(self, verbose: bool = False):
        """
        Initialize the multi-solver.

        Args:
            verbose: bool - If True, print detailed solver output (default False)
        """
        self.verbose = verbose

    def solve_all(self, problems: List[LinearProblem]) -> MultiSolverResult:
        """
        Solve all given problems.

        Args:
            problems: List[LinearProblem] - Problems to solve.

        Returns:
            MultiSolverResult with results for each problem.
        """
        result = MultiSolverResult(verbose=self.verbose)
        overall_start = time.perf_counter()

        for i, problem in enumerate(problems):
            problem_result = self._solve_single(problem, i + 1)
            result.results.append(problem_result)
            result.total_parse_time += problem_result.parse_time
            result.total_build_time += problem_result.build_time
            result.total_solve_time += problem_result.solve_time

        result.total_time = time.perf_counter() - overall_start
        return result

    def _solve_single(
        self, problem: LinearProblem, index: int
    ) -> ProblemResult:
        """Solve a single problem."""
        result = ProblemResult(problem=problem, solution=Solution(
            status="",
            objective_value=None,
            variables={}
        ))

        try:
            build_start = time.perf_counter()
            lp = LPBuilder(problem).build()
            result.build_time = time.perf_counter() - build_start

            solve_start = time.perf_counter()
            config = SolverConfig(verbose=self.verbose)
            solver = SolverLP(lp, config=config)
            solution = solver.solve()
            result.solution = solution
            result.solve_time = time.perf_counter() - solve_start

            result.total_time = (
                result.parse_time +
                result.build_time +
                result.solve_time
            )

        except Exception as e:
            result.error = str(e)
            result.solution.status = f"ERROR: {e}"

        return result

    @staticmethod
    def solve_from_text(text: str, verbose: bool = False) -> MultiSolverResult:
        """
        Parse and solve multiple problems from text.

        Args:
            text: str - Text with multiple problems separated by delimiters.
            verbose: bool - If True, print detailed solver output (default False)

        Returns:
            MultiSolverResult with results.
        """
        overall_start = time.perf_counter()

        parse_start = time.perf_counter()
        parser = MultiLPParser(text)
        problems = parser.parse_all()
        parse_time = time.perf_counter() - parse_start

        if not problems:
            result = MultiSolverResult(verbose=verbose)
            result.total_time = time.perf_counter() - overall_start
            return result

        solver = MultiSolver(verbose=verbose)
        result = solver.solve_all(problems)
        result.total_parse_time = parse_time

        return result