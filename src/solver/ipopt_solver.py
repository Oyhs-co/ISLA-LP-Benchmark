"""
Solver Ipopt para problemas de programacion lineal.
Implementacion usando cyipopt (interfaz Python a Ipopt).
"""

import time
from typing import Optional

from ..core import LinearProblem, Solution
from .base import BaseSolver, SolverStats


class IpoptSolver(BaseSolver):
    """Solver Ipopt para problemas de programacion lineal.

    ### atributos:
    - problem: LinearProblem - Problema a resolver.
    - config: Config - Configuracion del solver.
    """

    @property
    def solver_name(self) -> str:
        return "ipopt"

    @property
    def solver_version(self) -> str:
        try:
            import cyipopt
            return getattr(cyipopt, "__version__", "cyipopt")
        except ImportError:
            return "cyipopt (not installed)"

    @property
    def is_available(self) -> bool:
        try:
            import cyipopt
            return True
        except ImportError:
            return False

    def solve(self) -> Solution:
        """Resuelve el problema usando Ipopt.

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
            import cyipopt
        except ImportError as e:
            return Solution(
                status=f"ERROR: cyipopt not available: {e}",
                objective_value=None,
                variables={},
            )

        try:
            if problem.is_mip:
                return Solution(
                    status="ERROR: Ipopt does not support MIP",
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

            lb = np.full(n, -1e19, dtype=float)
            ub = np.full(n, 1e19, dtype=float)

            for var in variables_list:
                bound = problem.bounds.get(var)
                idx = variables_list.index(var)
                if bound:
                    if bound.lower is not None:
                        lb[idx] = bound.lower
                    if bound.upper is not None:
                        ub[idx] = bound.upper

            m = len(problem.constraints)
            cl = np.full(m, -1e19, dtype=float)
            cu = np.full(m, 1e19, dtype=float)

            A_rows = []
            for i, constr in enumerate(problem.constraints):
                coeffs = [constr.coefficients.get(v, 0.0) for v in variables_list]
                A_rows.append(coeffs)
                if constr.sense == "=":
                    cl[i] = constr.rhs
                    cu[i] = constr.rhs
                elif constr.sense in ("<=", "<"):
                    cu[i] = constr.rhs
                else:
                    cl[i] = constr.rhs

            A = np.array(A_rows, dtype=float)

            class LpProblem:
                def __init__(self, c_mat, A_mat):
                    self.c_mat = c_mat
                    self.A_mat = A_mat

                def objective(self, x):
                    return float(self.c_mat @ x)

                def gradient(self, x):
                    return self.c_mat

                def constraints(self, x):
                    return self.A_mat @ x

                def jacobian(self, x):
                    return self.A_mat

                def hessianstructure(self):
                    return np.array([], dtype=int), np.array([], dtype=int)

                def hessian(self, x, sigma, lambda_):
                    return np.array([], dtype=float)

            nlp_obj = LpProblem(c, A)

            nlp = cyipopt.Problem(
                n=n,
                m=m,
                problem_obj=nlp_obj,
                lb=lb.tolist() if hasattr(lb, 'tolist') else lb,
                ub=ub.tolist() if hasattr(ub, 'tolist') else ub,
                cl=cl.tolist() if hasattr(cl, 'tolist') else cl,
                cu=cu.tolist() if hasattr(cu, 'tolist') else cu,
            )

            nlp.add_option("print_level", 0)
            if self.config.verbose:
                nlp.add_option("print_level", 5)

            if self.config.time_limit is not None and self.config.time_limit > 0:
                nlp.add_option("max_cpu_time", self.config.time_limit)

            x0 = np.zeros(n)
            x, info = nlp.solve(x0)

            solve_time = time.perf_counter() - start_time

            ipopt_status = info.get("status", -1)
            if ipopt_status == 0:
                status = "OPTIMAL"
            elif ipopt_status in (1, 2):
                status = "OPTIMAL (TOLERANCE)"
            elif ipopt_status == -1:
                status = "ERROR: maximum iterations"
            elif ipopt_status in (-2, -12):
                status = "INFEASIBLE"
            elif ipopt_status in (-3, -11):
                status = "UNBOUNDED"
            elif ipopt_status == -10:
                status = "ERROR: insufficient memory"
            elif ipopt_status == -13:
                status = "ERROR: IPOPT problem too large"
            elif ipopt_status == -102:
                status = "TIME_LIMIT"
            else:
                status = f"ERROR: Ipopt status {ipopt_status}"
                try:
                    status_msg = nlp.get_info(7)
                    if status_msg:
                        status = f"ERROR: {status_msg}"
                except Exception:
                    pass

            variables = {}
            dual_values = None
            objective_value = None

            if status.startswith("OPTIMAL"):
                for i, var in enumerate(variables_list):
                    variables[var] = float(x[i])

                obj_val = float(c @ x)
                if problem.sense.lower() == "max":
                    obj_val = -obj_val
                objective_value = obj_val

                lambda_ = info.get("mult_g", None)
                if lambda_ is not None:
                    dual_values = {}
                    for i, constr in enumerate(problem.constraints):
                        if i < len(lambda_):
                            name = constr.name or f"R{i}"
                            dual_values[name] = float(lambda_[i])

            return Solution(
                status=status,
                objective_value=objective_value,
                variables=variables,
                dual_values=dual_values,
                reduced_costs=None,
                iterations=int(info.get("iter", 0)),
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
