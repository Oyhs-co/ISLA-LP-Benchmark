"""
Solver CVXOPT para problemas de programacion lineal.
Implementacion usando cvxopt (solvers.lp).
"""

import time

try:
    import cvxopt
    _is_solver_available = True
except ImportError:
    _is_solver_available = False

from ..core import LinearProblem, Solution
from .base import BaseSolver, SolverStats


class CVXOPTSolver(BaseSolver):
    """Solver CVXOPT para problemas de programacion lineal.
    """

    @property
    def solver_name(self) -> str:
        return "cvxopt"

    @property
    def solver_version(self) -> str:
        if _is_solver_available:
            try:
                return cvxopt.__version__
            except:
                return "cvxopt"
        return "cvxopt (not installed)"

    @property
    def is_available(self) -> bool:
        return _is_solver_available

    def solve(self) -> Solution:
        """Resuelve el problema usando CVXOPT.

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
            from cvxopt import matrix, solvers as cvx_solvers
        except ImportError as e:
            return Solution(
                status=f"ERROR: cvxopt not available: {e}",
                objective_value=None,
                variables={},
            )

        try:
            if problem.is_mip:
                return Solution(
                    status="ERROR: CVXOPT does not support MIP",
                    objective_value=None,
                    variables={},
                )

            variables_list = list(problem.variables)
            n = len(variables_list)

            c = np.array(
                [problem.objective.get(v, 0.0) for v in variables_list],
                dtype=float,
            )
            if problem.sense.lower() == "max":
                c = -c

            G_rows = []
            h_vals = []
            constraint_order = []

            for constr in problem.constraints:
                name = constr.name or f"R{problem.constraints.index(constr)}"
                coeffs = [constr.coefficients.get(v, 0.0) for v in variables_list]
                if constr.sense == "=":
                    continue
                if constr.sense in (">=", ">"):
                    G_rows.append([-x for x in coeffs])
                    h_vals.append(-constr.rhs)
                else:
                    G_rows.append(coeffs)
                    h_vals.append(constr.rhs)
                constraint_order.append(name)

            for var in variables_list:
                bound = problem.bounds.get(var)
                if bound:
                    idx = variables_list.index(var)
                    if bound.lower is not None:
                        row = [0.0] * n
                        row[idx] = -1.0
                        G_rows.append(row)
                        h_vals.append(-bound.lower)
                    if bound.upper is not None:
                        row = [0.0] * n
                        row[idx] = 1.0
                        G_rows.append(row)
                        h_vals.append(bound.upper)

            equality_rows = []
            equality_rhs = []
            for constr in problem.constraints:
                if constr.sense == "=":
                    equality_rows.append(
                        [constr.coefficients.get(v, 0.0) for v in variables_list]
                    )
                    equality_rhs.append(constr.rhs)

            cvx_solvers.options["show_progress"] = self.config.verbose

            c_m = matrix(c)

            if G_rows:
                G_m = matrix(np.array(G_rows, dtype=float))
                h_m = matrix(np.array(h_vals, dtype=float))
            else:
                G_m = None
                h_m = None

            if equality_rows:
                A_m = matrix(np.array(equality_rows, dtype=float))
                b_m = matrix(np.array(equality_rhs, dtype=float))
            else:
                A_m = None
                b_m = None

            sol = cvx_solvers.lp(c_m, G_m, h_m, A_m, b_m)

            solve_time = time.perf_counter() - start_time

            cvx_status = sol["status"]
            if cvx_status == "optimal":
                status = "OPTIMAL"
            elif cvx_status == "primal infeasible":
                status = "INFEASIBLE"
            elif cvx_status == "dual infeasible":
                status = "UNBOUNDED"
            else:
                status = f"ERROR: {cvx_status}"

            variables = {}
            dual_values = None
            objective_value = None

            if status == "OPTIMAL":
                x = sol["x"]
                for i, var in enumerate(variables_list):
                    variables[var] = float(x[i])

                objective_value = float(sol["primal objective"])
                if problem.sense.lower() == "max":
                    objective_value = -objective_value

                z = sol.get("z")
                if z is not None and len(z) > 0 and constraint_order:
                    dual_values = {}
                    for i, name in enumerate(constraint_order):
                        if i < len(z):
                            dual_values[name] = float(z[i])

            return Solution(
                status=status,
                objective_value=objective_value,
                variables=variables,
                dual_values=dual_values,
                reduced_costs=None,
                iterations=int(sol.get("iterations", 0)),
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
