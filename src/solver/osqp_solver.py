"""
Solver OSQP para problemas de programacion lineal.
Implementacion usando osqp (Operator Splitting QP Solver).
"""

import time

try:
    import osqp
    _is_solver_available = True
except ImportError:
    _is_solver_available = False

from typing import Optional

from ..core import LinearProblem, Solution
from .base import BaseSolver, SolverStats, SolverCapabilities


class OSQPSolver(BaseSolver):
    """Solver OSQP para problemas de programacion lineal.
    """

    def __init__(self, problem: LinearProblem, config: Optional[BaseSolver.Config] = None):
        super().__init__(problem, config)
        self.capabilities = SolverCapabilities(
            lp=True,
            milp=False,
            qp=True,
            duals=True,
            warm_start=True,
            sensitivity=False
        )

    @property
    def solver_name(self) -> str:
        return "osqp"

    @property
    def solver_version(self) -> str:
        if _is_solver_available:
            try:
                return osqp.__version__
            except:
                return "osqp"
        return "osqp (not installed)"

    @property
    def is_available(self) -> bool:
        return _is_solver_available

    def solve(self) -> Solution:
        """Resuelve el problema usando OSQP.

        Returns:
            Solution: Objeto con la solucion del problema.
        """
        problem = self.problem

        if problem is None:
            return Solution(
                status="ERROR: No problem set",
                objective_value=None,
                variables={},
            )

        start_time = time.perf_counter()

        try:
            import numpy as np
            from scipy import sparse
            import osqp
        except ImportError as e:
            return Solution(
                status=f"ERROR: osqp not available: {e}",
                objective_value=None,
                variables={},
            )

        try:
            if problem.is_mip:
                return Solution(
                    status="ERROR: OSQP does not support MIP",
                    objective_value=None,
                    variables={},
                )

            variables_list = list(problem.variables)
            n = len(variables_list)

            q = np.array(
                [problem.objective.get(v, 0.0) for v in variables_list],
                dtype=float,
            )
            if problem.sense.lower() == "max":
                q = -q

            A_rows = []
            l_vals = []
            u_vals = []
            constraint_order = []

            for constr in problem.constraints:
                name = constr.name or f"R{problem.constraints.index(constr)}"
                coeffs = [constr.coefficients.get(v, 0.0) for v in variables_list]
                if constr.sense == "=":
                    A_rows.append(coeffs)
                    l_vals.append(constr.rhs)
                    u_vals.append(constr.rhs)
                elif constr.sense in ("<=", "<"):
                    A_rows.append(coeffs)
                    l_vals.append(-np.inf)
                    u_vals.append(constr.rhs)
                else:
                    A_rows.append(coeffs)
                    l_vals.append(constr.rhs)
                    u_vals.append(np.inf)
                constraint_order.append(name)

            for var in variables_list:
                bound = problem.bounds.get(var)
                if bound:
                    row = [0.0] * n
                    row[variables_list.index(var)] = 1.0
                    A_rows.append(row)
                    lb = bound.lower if bound.lower is not None else -np.inf
                    ub = bound.upper if bound.upper is not None else np.inf
                    l_vals.append(lb)
                    u_vals.append(ub)

            if not A_rows:
                A = sparse.csc_matrix((0, n))
                l = np.array([])
                u = np.array([])
            else:
                A = sparse.csc_matrix(np.array(A_rows, dtype=float))
                l = np.array(l_vals, dtype=float)
                u = np.array(u_vals, dtype=float)

            P = sparse.csc_matrix((n, n))

            settings = {
                "verbose": self.config.verbose,
                "eps_abs": 1e-8,
                "eps_rel": 1e-8,
                "max_iter": 10000,
            }
            if self.config.time_limit is not None and self.config.time_limit > 0:
                settings["time_limit"] = self.config.time_limit

            solver = osqp.OSQP()
            solver.setup(P, q, A, l, u, **settings)
            res = solver.solve()

            solve_time = time.perf_counter() - start_time

            info_status = res.info.status
            if info_status == "solved":
                status = "OPTIMAL"
            elif info_status == "solved inaccurate":
                status = "OPTIMAL (INACCURATE)"
            elif "primal infeasible" in info_status:
                status = "INFEASIBLE"
            elif "dual infeasible" in info_status:
                status = "UNBOUNDED"
            elif "interrupted" in info_status or "time limit" in info_status:
                status = "TIME_LIMIT"
            else:
                status = f"ERROR: {info_status}"

            variables = {}
            dual_values = None
            objective_value = None

            if status.startswith("OPTIMAL"):
                x = res.x
                for i, var in enumerate(variables_list):
                    variables[var] = float(x[i])

                objective_value = float(res.info.obj_val)
                if problem.sense.lower() == "max":
                    objective_value = -objective_value

                y = res.y
                if y is not None:
                    dual_values = {}
                    for i, name in enumerate(constraint_order):
                        if i < len(y):
                            dual_values[name] = float(y[i])

            return Solution(
                status=status,
                objective_value=objective_value,
                variables=variables,
                dual_values=dual_values,
                reduced_costs=None,
                iterations=int(res.info.iter),
            )

        except Exception as e:
            return Solution(
                status=f"ERROR: {str(e)}",
                objective_value=None,
                variables={},
            )

    def get_stats(self) -> SolverStats:
        """Obtiene estadisticas de la ultima ejecucion."""
        return SolverStats(
            iterations=0,
            nodes=0,
        )
