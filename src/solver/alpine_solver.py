"""
Solver Alpine para problemas de programacion lineal.
Implementacion usando pyoptinterface como backend moderno y ligero.
"""

import time

from ..core import LinearProblem, Solution
from .base import BaseSolver, SolverStats


class AlpineSolver(BaseSolver):
    """Solver Alpine para problemas de programacion lineal.

    ### atributos:
    - problem: LinearProblem - Problema a resolver.
    - config: Config - Configuracion del solver.
    """

    @property
    def solver_name(self) -> str:
        return "alpine"

    @property
    def solver_version(self) -> str:
        try:
            import pyoptinterface as poi
            return getattr(poi, "__version__", "pyoptinterface")
        except ImportError:
            return "pyoptinterface (not installed)"

    @property
    def is_available(self) -> bool:
        try:
            import pyoptinterface
            return True
        except ImportError:
            return False

    def solve(self) -> Solution:
        """Resuelve el problema usando PyOptInterface.

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
            import pyoptinterface as poi
            from pyoptinterface import highs
        except ImportError as e:
            return Solution(
                status=f"ERROR: pyoptinterface not available: {e}",
                objective_value=None,
                variables={},
            )

        try:
            variables_list = list(problem.variables)
            n = len(variables_list)

            model = highs.Model()
            model.setModelAttribute(
                poi.ModelAttribute.Sense,
                poi.ObjectiveSense.Maximize
                if problem.sense.lower() == "max"
                else poi.ObjectiveSense.Minimize,
            )

            poi_vars = {}
            for var in variables_list:
                bound = problem.bounds.get(var)
                lb = bound.lower if bound and bound.lower is not None else -1e30
                ub = bound.upper if bound and bound.upper is not None else 1e30

                vtype = poi.VariableDomain.Continuous
                var_type = problem.variable_types.get(var, "continuous")
                if var_type == "integer":
                    vtype = poi.VariableDomain.Integer
                elif var_type == "binary":
                    vtype = poi.VariableDomain.Binary
                    lb = 0.0
                    ub = 1.0

                poi_vars[var] = model.addVariable(
                    lb=lb, ub=ub, domain=vtype,
                )

            obj_expr = poi.ExprBuilder()
            for var in variables_list:
                coeff = problem.objective.get(var, 0.0)
                if coeff != 0:
                    obj_expr.add(poi_vars[var], coeff)
            model.setObjective(obj_expr)

            for constr in problem.constraints:
                expr = poi.ExprBuilder()
                for var, coeff in constr.coefficients.items():
                    if coeff != 0:
                        expr.add(poi_vars[var], coeff)

                if constr.sense == "=":
                    model.addLinearConstraint(expr, poi.Eq(constr.rhs))
                elif constr.sense in ("<=", "<"):
                    model.addLinearConstraint(expr, poi.Leq(constr.rhs))
                else:
                    model.addLinearConstraint(expr, poi.Geq(constr.rhs))

            model.optimize()

            solve_time = time.perf_counter() - start_time

            term_status = model.getModelAttribute(poi.ModelAttribute.TerminationStatus)
            result_status = model.getModelAttribute(poi.ModelAttribute.ResultStatus)

            if term_status == poi.TerminationStatusCode.Optimal:
                status = "OPTIMAL"
            elif term_status in (
                poi.TerminationStatusCode.Infeasible,
                poi.TerminationStatusCode.InfeasibleOrUnbounded,
            ):
                status = "INFEASIBLE"
            elif term_status == poi.TerminationStatusCode.Unbounded:
                status = "UNBOUNDED"
            elif term_status == poi.TerminationStatusCode.TimeLimit:
                status = "TIME_LIMIT"
            else:
                status = f"ERROR: term={term_status} result={result_status}"

            variables = {}
            dual_values = None
            reduced_costs = None
            objective_value = None

            if status == "OPTIMAL":
                obj_val = model.getModelAttribute(poi.ModelAttribute.ObjectiveValue)
                objective_value = float(obj_val)

                for var in variables_list:
                    val = model.getVariableAttribute(
                        poi.VariableAttribute.Value, poi_vars[var]
                    )
                    variables[var] = float(val)

                try:
                    dual_values = {}
                    for constr in problem.constraints:
                        pass
                except Exception:
                    dual_values = None

                try:
                    reduced_costs = {}
                    for var in variables_list:
                        rc = model.getVariableAttribute(
                            poi.VariableAttribute.ReducedCost, poi_vars[var]
                        )
                        reduced_costs[var] = float(rc)
                except Exception:
                    reduced_costs = None

            return Solution(
                status=status,
                objective_value=objective_value,
                variables=variables,
                dual_values=dual_values,
                reduced_costs=reduced_costs,
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
