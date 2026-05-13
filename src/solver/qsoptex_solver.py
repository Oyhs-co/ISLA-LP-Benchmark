"""
Solver QSopt_ex para problemas de programacion lineal.
Implementacion usando bindings nativos qsopt-python (COIN-OR).
"""

import time

from ..core import LinearProblem, Solution
from .base import BaseSolver, SolverStats


class QSoptExSolver(BaseSolver):
    """Solver QSopt_ex para problemas de programacion lineal.

    ### atributos:
    - problem: LinearProblem - Problema a resolver.
    - config: Config - Configuracion del solver.
    """

    @property
    def solver_name(self) -> str:
        return "qsopt_ex"

    @property
    def solver_version(self) -> str:
        return "qsopt-python (academic)"

    @property
    def is_available(self) -> bool:
        try:
            import qsopt
            return True
        except ImportError:
            return False

    def solve(self) -> Solution:
        """Resuelve el problema usando QSopt_ex.

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
            import qsopt
        except ImportError:
            return Solution(
                status="ERROR: QSopt_ex not available. "
                       "Install qsopt-python from COIN-OR (academic license)",
                objective_value=None,
                variables={},
            )

        try:
            if problem.is_mip:
                return Solution(
                    status="ERROR: QSopt_ex MILP not yet supported via Python bindings",
                    objective_value=None,
                    variables={},
                )

            variables_list = list(problem.variables)
            n = len(variables_list)

            c = [
                problem.objective.get(v, 0.0)
                for v in variables_list
            ]
            if problem.sense.lower() == "max":
                c = [-x for x in c]

            obj = {"objective": c}

            A_rows = []
            b_vals = []
            sense_chars = []
            constraint_names = []

            for constr in problem.constraints:
                name = constr.name or f"R{problem.constraints.index(constr)}"
                coeffs = [constr.coefficients.get(v, 0.0) for v in variables_list]
                A_rows.append(coeffs)
                b_vals.append(constr.rhs)
                if constr.sense == "=":
                    sense_chars.append("E")
                elif constr.sense in ("<=", "<"):
                    sense_chars.append("L")
                else:
                    sense_chars.append("G")
                constraint_names.append(name)

            for var in variables_list:
                bound = problem.bounds.get(var)
                if bound:
                    idx = variables_list.index(var)
                    if bound.lower is not None:
                        row = [0.0] * n
                        row[idx] = -1.0
                        A_rows.append(row)
                        b_vals.append(-bound.lower)
                        sense_chars.append("L")
                    if bound.upper is not None:
                        row = [0.0] * n
                        row[idx] = 1.0
                        A_rows.append(row)
                        b_vals.append(bound.upper)
                        sense_chars.append("L")

            m = len(A_rows)
            if m == 0:
                return Solution(
                    status="ERROR: No constraints defined",
                    objective_value=None,
                    variables={},
                )

            numnz = sum(1 for row in A_rows for coeff in row if coeff != 0)
            begin = []
            ind = []
            val = []
            nz_count = 0
            for row in A_rows:
                begin.append(nz_count)
                for j, coeff in enumerate(row):
                    if coeff != 0:
                        ind.append(j)
                        val.append(coeff)
                        nz_count += 1
            begin.append(nz_count)

            try:
                lp = qsopt.QSload_prob(n, m, numnz, begin, ind, val, b_vals, sense_chars)
            except AttributeError:
                return Solution(
                    status="ERROR: QSopt_ex Python API mismatch. "
                           "Expected qsopt.QSload_prob interface",
                    objective_value=None,
                    variables={},
                )

            try:
                qsopt.QSset_maxmin(lp, 1)
                qsopt.QSoptimize(lp)
            except AttributeError:
                try:
                    qsopt.QSopt_maxmin(lp, 1)
                    qsopt.QSopt_optimize(lp)
                except AttributeError:
                    return Solution(
                        status="ERROR: QSopt_ex optimization functions not found",
                        objective_value=None,
                        variables={},
                    )

            solve_time = time.perf_counter() - start_time

            try:
                status_val = qsopt.QSget_status(lp)
            except AttributeError:
                status = "ERROR: QSopt_ex status function not found"
                status_val = -1

            if status_val == 0:
                status = "OPTIMAL"
            elif status_val == 1:
                status = "INFEASIBLE"
            elif status_val == 2:
                status = "UNBOUNDED"
            else:
                status = f"ERROR: QSopt_ex status={status_val}"

            variables = {}
            objective_value = None

            if status == "OPTIMAL":
                try:
                    x = qsopt.QSget_x(lp)
                    for i, var in enumerate(variables_list):
                        variables[var] = float(x[i])
                    objective_value = float(qsopt.QSget_objval(lp))
                    if problem.sense.lower() == "max":
                        objective_value = -objective_value
                except AttributeError:
                    pass

            return Solution(
                status=status,
                objective_value=objective_value,
                variables=variables,
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
