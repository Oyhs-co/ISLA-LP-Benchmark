"""
Solver Couenne para problemas de programacion lineal.
Implementacion usando Pyomo como interfaz a Couenne (COIN-OR).
"""

import time

from ..core import LinearProblem, Solution
from .base import BaseSolver, SolverStats


class CouenneSolver(BaseSolver):
    """Solver Couenne para problemas de programacion lineal.

    ### atributos:
    - problem: LinearProblem - Problema a resolver.
    - config: Config - Configuracion del solver.
    """

    @property
    def solver_name(self) -> str:
        return "couenne"

    @property
    def solver_version(self) -> str:
        try:
            from pyomo.opt import SolverFactory
            opt = SolverFactory("couenne")
            return getattr(opt, "version", "couenne")
        except Exception:
            return "couenne (not available)"

    @property
    def is_available(self) -> bool:
        try:
            from pyomo.opt import SolverFactory
            opt = SolverFactory("couenne")
            return opt.available(exception_flag=False)
        except Exception:
            return False

    def _build_pyomo_model(self):
        import pyomo.environ as pyo
        problem = self.problem
        variables_list = list(problem.variables)

        model = pyo.ConcreteModel()
        model.vars = pyo.Var(variables_list, domain=pyo.Reals)

        for var in variables_list:
            vtype = problem.variable_types.get(var, "continuous")
            if vtype == "integer":
                model.vars[var].domain = pyo.Integer
            elif vtype == "binary":
                model.vars[var].domain = pyo.Binary
            bound = problem.bounds.get(var)
            if bound:
                if bound.lower is not None:
                    model.vars[var].setlb(bound.lower)
                if bound.upper is not None:
                    model.vars[var].setub(bound.upper)

        obj_expr = sum(
            problem.objective.get(v, 0.0) * model.vars[v]
            for v in variables_list
        )
        if problem.sense.lower() == "max":
            model.obj = pyo.Objective(expr=obj_expr, sense=pyo.maximize)
        else:
            model.obj = pyo.Objective(expr=obj_expr, sense=pyo.minimize)

        for constr in problem.constraints:
            expr = sum(
                constr.coefficients.get(v, 0.0) * model.vars[v]
                for v in variables_list
            )
            if constr.sense == "=":
                model.add_component(
                    constr.name or f"c{problem.constraints.index(constr)}",
                    pyo.Constraint(expr=expr == constr.rhs),
                )
            elif constr.sense in ("<=", "<"):
                model.add_component(
                    constr.name or f"c{problem.constraints.index(constr)}",
                    pyo.Constraint(expr=expr <= constr.rhs),
                )
            else:
                model.add_component(
                    constr.name or f"c{problem.constraints.index(constr)}",
                    pyo.Constraint(expr=expr >= constr.rhs),
                )

        return model

    def solve(self) -> Solution:
        """Resuelve el problema usando Couenne.

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
            import pyomo.environ as pyo
            from pyomo.opt import SolverFactory
        except ImportError as e:
            return Solution(
                status=f"ERROR: pyomo not available: {e}",
                objective_value=None,
                variables={},
            )

        try:
            variables_list = list(problem.variables)
            model = self._build_pyomo_model()
            opt = SolverFactory("couenne")
            if not opt.available(exception_flag=False):
                return Solution(
                    status="ERROR: Couenne solver executable not found",
                    objective_value=None,
                    variables={},
                )

            if self.config.time_limit is not None and self.config.time_limit > 0:
                opt.options["time_limit"] = self.config.time_limit

            result = opt.solve(model, tee=self.config.verbose)
            solve_time = time.perf_counter() - start_time

            term = result.solver.termination_condition
            if term == pyo.TerminationCondition.optimal:
                status = "OPTIMAL"
            elif term in (
                pyo.TerminationCondition.infeasible,
                pyo.TerminationCondition.infeasibleOrUnbounded,
            ):
                status = "INFEASIBLE"
            elif term == pyo.TerminationCondition.unbounded:
                status = "UNBOUNDED"
            elif term == pyo.TerminationCondition.maxTimeLimit:
                status = "TIME_LIMIT"
            else:
                status = f"ERROR: {term}"

            variables = {}
            objective_value = None
            if status == "OPTIMAL":
                objective_value = float(pyo.value(model.obj))
                for var in variables_list:
                    variables[var] = float(pyo.value(model.vars[var]))

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
        return SolverStats(iterations=0, nodes=0)
