"""
Modulo de solvers para programacion lineal.
Proporciona interfaz abstracta y implementaciones concretas.
"""

from .base import BaseSolver, SolverStats, SolverRegistry, register_solver
from .gurobi import GurobiSolver
from .multi_solver import MultiSolver, MultiSolverResult, ProblemResult
from .benchmark import BenchmarkRunner, BenchmarkResult, BenchmarkConfig, run_quick_benchmark

SolverLP = GurobiSolver
SolverConfig = GurobiSolver.Config

SolverRegistry.register("gurobi", GurobiSolver, available=True)

try:
    from .highs_solver import HiGHSSolver
    SolverRegistry.register("highs", HiGHSSolver, available=True)
except ImportError as e:
    import types
    class HiGHSSolver:
        pass
    HiGHSSolver.solver_name = "highs"
    HiGHSSolver.__name__ = "HiGHSSolver"
    SolverRegistry.register("highs", HiGHSSolver, available=False)
    SolverRegistry.set_unavailable("highs", f"highspy not available: {e}")

try:
    from .glpk_solver import GLPKSolver
    SolverRegistry.register("glpk", GLPKSolver, available=True)
except ImportError as e:
    import types
    class GLPKSolver:
        pass
    GLPKSolver.solver_name = "glpk"
    GLPKSolver.__name__ = "GLPKSolver"
    SolverRegistry.register("glpk", GLPKSolver, available=False)
    SolverRegistry.set_unavailable("glpk", f"swiglpk not available: {e}")

try:
    from .cbc import CBCSolver
    import pulp
    if "PULP_CBC_CMD" in pulp.listSolvers():
        SolverRegistry.register("cbc", CBCSolver, available=True)
    else:
        SolverRegistry.register("cbc", CBCSolver, available=False)
        SolverRegistry.set_unavailable("cbc", "PULP_CBC_CMD not found")
except ImportError as e:
    import types
    class CBCSolver:
        pass
    CBCSolver.solver_name = "cbc"
    CBCSolver.__name__ = "CBCSolver"
    SolverRegistry.register("cbc", CBCSolver, available=False)
    SolverRegistry.set_unavailable("cbc", f"not available: {e}")

# F4-3: Register SCIP solver
try:
    from .scip import SCIPSolver
    SolverRegistry.register("scip", SCIPSolver, available=True)
except ImportError as e:
    import types
    class SCIPSolver:
        pass
    SCIPSolver.solver_name = "scip"
    SCIPSolver.__name__ = "SCIPSolver"
    SolverRegistry.register("scip", SCIPSolver, available=False)
    SolverRegistry.set_unavailable("scip", f"pyscipopt not available: {e}")

# F7-1: Register ECOS solver
try:
    from .ecos import ECOSSolver
    SolverRegistry.register("ecos", ECOSSolver, available=True)
except ImportError as e:
    import types
    class ECOSSolver:
        pass
    ECOSSolver.solver_name = "ecos"
    ECOSSolver.__name__ = "ECOSSolver"
    SolverRegistry.register("ecos", ECOSSolver, available=False)
    SolverRegistry.set_unavailable("ecos", f"ecos not available: {e}")

# F7-2: Register OSQP solver
try:
    from .osqp_solver import OSQPSolver
    SolverRegistry.register("osqp", OSQPSolver, available=True)
except ImportError as e:
    import types
    class OSQPSolver:
        pass
    OSQPSolver.solver_name = "osqp"
    OSQPSolver.__name__ = "OSQPSolver"
    SolverRegistry.register("osqp", OSQPSolver, available=False)
    SolverRegistry.set_unavailable("osqp", f"osqp not available: {e}")

# F7-3: Register CVXOPT solver
try:
    from .cvxopt_solver import CVXOPTSolver
    SolverRegistry.register("cvxopt", CVXOPTSolver, available=True)
except ImportError as e:
    import types
    class CVXOPTSolver:
        pass
    CVXOPTSolver.solver_name = "cvxopt"
    CVXOPTSolver.__name__ = "CVXOPTSolver"
    SolverRegistry.register("cvxopt", CVXOPTSolver, available=False)
    SolverRegistry.set_unavailable("cvxopt", f"cvxopt not available: {e}")

# F7-4: Register SCS solver
try:
    from .scs_solver import SCSSolver
    SolverRegistry.register("scs", SCSSolver, available=True)
except ImportError as e:
    import types
    class SCSSolver:
        pass
    SCSSolver.solver_name = "scs"
    SCSSolver.__name__ = "SCSSolver"
    SolverRegistry.register("scs", SCSSolver, available=False)
    SolverRegistry.set_unavailable("scs", f"scs not available: {e}")

# F7-5: Register Ipopt solver
try:
    from .ipopt_solver import IpoptSolver
    SolverRegistry.register("ipopt", IpoptSolver, available=True)
except ImportError as e:
    import types
    class IpoptSolver:
        pass
    IpoptSolver.solver_name = "ipopt"
    IpoptSolver.__name__ = "IpoptSolver"
    SolverRegistry.register("ipopt", IpoptSolver, available=False)
    SolverRegistry.set_unavailable("ipopt", f"cyipopt not available: {e}")

# F7-6: Register Alpine solver (via PyOptInterface)
try:
    from .alpine_solver import AlpineSolver
    SolverRegistry.register("alpine", AlpineSolver, available=True)
except ImportError as e:
    import types
    class AlpineSolver:
        pass
    AlpineSolver.solver_name = "alpine"
    AlpineSolver.__name__ = "AlpineSolver"
    SolverRegistry.register("alpine", AlpineSolver, available=False)
    SolverRegistry.set_unavailable("alpine", f"pyoptinterface not available: {e}")

# F7-7: Register Bonmin solver (via Pyomo)
try:
    from .bonmin_solver import BonminSolver
    SolverRegistry.register("bonmin", BonminSolver, available=True)
except ImportError as e:
    import types
    class BonminSolver:
        pass
    BonminSolver.solver_name = "bonmin"
    BonminSolver.__name__ = "BonminSolver"
    SolverRegistry.register("bonmin", BonminSolver, available=False)
    SolverRegistry.set_unavailable("bonmin", f"pyomo not available: {e}")

# F7-8: Register Couenne solver (via Pyomo)
try:
    from .couenne_solver import CouenneSolver
    SolverRegistry.register("couenne", CouenneSolver, available=True)
except ImportError as e:
    import types
    class CouenneSolver:
        pass
    CouenneSolver.solver_name = "couenne"
    CouenneSolver.__name__ = "CouenneSolver"
    SolverRegistry.register("couenne", CouenneSolver, available=False)
    SolverRegistry.set_unavailable("couenne", f"pyomo not available: {e}")

# F7-9: Register Symphony solver (via Pyomo)
try:
    from .symphony_solver import SymphonySolver
    SolverRegistry.register("symphony", SymphonySolver, available=True)
except ImportError as e:
    import types
    class SymphonySolver:
        pass
    SymphonySolver.solver_name = "symphony"
    SymphonySolver.__name__ = "SymphonySolver"
    SolverRegistry.register("symphony", SymphonySolver, available=False)
    SolverRegistry.set_unavailable("symphony", f"pyomo not available: {e}")

# F7-10: Register QSopt_ex solver
try:
    from .qsoptex_solver import QSoptExSolver
    SolverRegistry.register("qsopt_ex", QSoptExSolver, available=True)
except ImportError as e:
    import types
    class QSoptExSolver:
        pass
    QSoptExSolver.solver_name = "qsopt_ex"
    QSoptExSolver.__name__ = "QSoptExSolver"
    SolverRegistry.register("qsopt_ex", QSoptExSolver, available=False)
    SolverRegistry.set_unavailable("qsopt_ex", f"qsopt-python not available: {e}")

__all__ = [
    "BaseSolver",
    "SolverStats", 
    "SolverRegistry",
    "register_solver",
    "GurobiSolver",
    "CBCSolver",
    "HiGHSSolver",
    "GLPKSolver",
    "ECOSSolver",
    "OSQPSolver",
    "CVXOPTSolver",
    "SCSSolver",
    "IpoptSolver",
    "AlpineSolver",
    "BonminSolver",
    "CouenneSolver",
    "SymphonySolver",
    "QSoptExSolver",
    "SolverLP",
    "SolverConfig",
    "MultiSolver",
    "MultiSolverResult", 
    "ProblemResult",
    "BenchmarkRunner",
    "BenchmarkResult",
    "BenchmarkConfig",
    "run_quick_benchmark"
]