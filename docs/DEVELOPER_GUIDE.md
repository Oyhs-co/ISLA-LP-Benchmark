# Guía del Desarrollador - ISLA LP Benchmark

Esta guía es para **desarrolladores** que quieren extender o integrar el proyecto.

## Arquitectura del Sistema

```
src/
├── cli/                      # Interfaz CLI
│   ├── __main__.py           # Punto de entrada
│   ├── benchmark.py         # Handler benchmark
│   ├── solve.py           # Handler resolución
│   └── __init__.py        # Utilidades sistema
├── solver/                  # Implementaciones de solvers
│   ├── base.py            # BaseSolver, SolverRegistry
│   ├── gurobi.py         # Solver Gurobi
│   ├── highs_solver.py    # Solver HiGHS (native)
│   ├── glpk_solver.py    # Solver GLPK (native)
│   ├── cbc.py           # Solver CBC (PuLP)
│   ├── benchmark.py     # BenchmarkRunner
│   └── __init__.py
├── analysis/               # Análisis y reportes
│   ├── analysis.py       # Reporte single
│   ├── benchmark_report.py  # Reporte PDF
│   ├── benchmark_results.py # Visualización
│   └── __init__.py
├── parser/                # Parsing de archivos
│   ├── lp_parser.py     # Formato texto
│   ├── cplex_parser.py # CPLEX/LP
│   └── __init__.py
├── core/                  # Modelos de datos
│   ├── problem.py      # LinearProblem
│   ├── constraint.py # LinearConstraint
│   ├── bound.py       # VariableBound
│   ├── solution.py    # Solution
│   └── __init__.py
├── matrix/                # Construcción Polars
│   ├── builder.py     # LPBuilder
│   ├── matrix.py     # PolarsLP
│   └── __init__.py
├── visualization/         # Gráficos
│   ├── visualization.py
│   └── __init__.py
└── utils/                 # Utilidades
    ├── validation.py
    ├── exporter.py
    ├── logging.py
    └── __init__.py
```

## Uso Básico

### Resolver un Problema

```python
from src.parser import LPParser
from src.matrix import LPBuilder
from src.solver import SolverRegistry

# Parsear
problem = LPParser(texto).parse()

# Construir
lp = LPBuilder(problem).build()

# Obtener solver
solver_class = SolverRegistry.get('highs')
solver = solver_class(lp)

# Resolver
solution = solver.solve()

# Resultados
print(solution.objective_value)
print(solution.variables)
```

### Modo Benchmark

```python
from src.solver import BenchmarkRunner, BenchmarkConfig

config = BenchmarkConfig(
    warmup_runs=1,
    runs_per_problem=3,
    verbose=False,
    collect_memory=True
)

runner = BenchmarkRunner(config)
problems = [("problema1", texto)]
solvers = ['highs', 'glpk', 'cbc']

results = runner.run(problems, solvers)

# Métricas
summary = runner.get_summary()
print(summary['by_solver'])
```

### Listar Solvers Disponibles

```python
from src.solver import SolverRegistry

# Lista de nombres
solvers = SolverRegistry.list_solvers()
print(solvers)  # ['gurobi', 'highs', 'glpk', 'cbc']

# Información detallada
all_info = SolverRegistry.list_all_info()
for name, info in all_info.items():
    print(f"{name}: {info['available']}")
```

## Registro de Solvers

### @register_solver Decorator

```python
from src.solver import BaseSolver, SolverStats, register_solver
from src.core import Solution, LinearProblem
from src.matrix import PolarsLP

@register_solver("mi_solver")
class MiSolver(BaseSolver):
    """ Implementación de solver personalizado """
    
    def __init__(self, model: PolarsLP, config=None):
        super().__init__(config)
        self.model = model
        self._solution = None
        self._linear_problem = None
    
    @property
    def solver_name(self) -> str:
        return "mi_solver"
    
    @property
    def solver_version(self) -> str:
        return "1.0.0"
    
    @property
    def is_available(self) -> bool:
        # Verificar disponibilidad
        return True
    
    def set_problem(self, problem: LinearProblem) -> None:
        self._linear_problem = problem
    
    def solve(self) -> Solution:
        # Resolver problema
        return Solution(
            status="OPTIMAL",
            objective_value=42.0,
            variables={"x": 1.0, "y": 2.0}
        )
    
    def get_stats(self) -> SolverStats:
        return SolverStats(iterations=2, nodes=0)
```

### Registro de SCIP

```python
from src.solver import SolverRegistry

# Verificar si SCIP está disponible
registry = SolverRegistry()
info = registry.list_all_info()
print(info.get('scip', {}).get('available', False))

# SCIP soporta MILP (integer, binary)
from src.solver import SCIPSolver
help(SCIPSolver)
```

## APIs Principales

### LinearProblem

```python
from src.core import LinearProblem, LinearConstraint, VariableBound

problem = LinearProblem(
    objective={"x": 3000, "y": 5000},
    sense="max",
    constraints=[
        LinearConstraint(
            coefficients={"x": 2, "y": 3},
            rhs=120,
            sense="<="
        )
    ],
    bounds={
        "x": VariableBound("x", 0, None),
        "y": VariableBound("y", 0, None)
    }
)
```

### Solution

```python
solution = Solution(
    status="OPTIMAL",
    objective_value=190000.0,
    variables={"x": 30.0, "y": 20.0},
    dual_values={"c1": 1000.0},
    reduced_costs={"x": 0.0, "y": 0.0}
)

# Verificar estado
solution.is_optimal()    # True
solution.is_infeasible() # False
solution.is_unbounded()   # False
```

### BenchmarkRunner

```python
runner = BenchmarkRunner(config)

# Agregar resultado
runner.results.append(BenchmarkResult(
    solver_name="highs",
    problem_name="problema1",
    problem_text=texto,
    solution=solution,
    stats=SolverStats(iterations=2, nodes=0),
    parse_time=0.001,
    build_time=0.002,
    solve_time=0.045,
    total_time=0.048,
    memory_used_mb=45.2,
    peak_memory_mb=52.1
))

# Exportar
runner.export_csv(Path("results.csv"))
runner.export_json(Path("results.json"))
```

## Verificación de Soluciones

### verify_solution()

```python
from src.core.verification import verify_solution, compare_solutions
from src.core import LinearProblem, Solution

# Verificar una solución
is_valid, issues = verify_solution(problem, solution)
if not is_valid:
    print("Problemas encontrados:")
    for issue in issues:
        print(f"  - {issue}")

# Comparar soluciones de múltiples solvers
solutions = [gurobi_sol, highs_sol, glpk_sol]
warnings = compare_solutions(problem, solutions)
for warning in warnings:
    print(f"ADVERTENCIA: {warning}")
```

**Tolerancias**: Usa `FEASIBILITY_TOLERANCE` (1e-6) por defecto.

## Exportación Avanzada

### ResultsExporter

```python
from src.analysis.benchmark_results import ResultsExporter, export_benchmark_results
from pathlib import Path

# Usando ResultsExporter
exporter = ResultsExporter(runner)
exporter.to_markdown(Path("report.md"))
exporter.to_html(Path("report.html"), include_plots=True, plots_dir=Path("plots"))

# Método rápido (recomendado)
paths = export_benchmark_results(
    runner=runner,
    output_dir=Path("data/benchmark_output"),
    formats=["json", "csv", "md", "html"],
    include_plots=True
)
# Retorna: {"json": Path(...), "csv": Path(...), "md": Path(...), "html": Path(...)}
```

## Análisis Multi-Problema

### MultiLPAnalysis

```python
from src.analysis.multi_analysis import MultiLPAnalysis
from src.solver import MultiSolverResult

# results: MultiSolverResult
analysis = MultiLPAnalysis(results)
analysis.generate_pdf("output/multi_report.pdf")
```

**Secciones del reporte**:
1. Portada con estadísticas
2. Resumen ejecutivo
3. Página individual por problema
4. Resumen de tiempos

---

## Extensiones

### Agregar Nuevo Parser

```python
# src/parser/mi_parser.py
from ..core import LinearProblem

class MiParser:
    def __init__(self, texto: str):
        self.texto = texto
    
    def parse(self) -> LinearProblem:
        # Lógica de parsing
        return LinearProblem(...)
```

### Agregar Visualización

```python
from src.analysis.benchmark_results import BenchmarkVisualizer

viz = BenchmarkVisualizer(runner)
viz.plot_times_comparison(save_path="times.png")
viz.plot_memory_comparison(save_path="memory.png")
```

## Patrones Comunes

### Manejo de Errores

```python
from src.core.exceptions import LPParseError, LPSolverError

try:
    problem = LPParser(texto).parse()
except LPParseError as e:
    print(f"Error de parseo: {e}")
```

### Verificar Solución

```python
solution = solver.solve()

if solution.is_optimal():
    print(f"Óptimo: {solution.objective_value}")
elif solution.is_infeasible():
    print("Problema infactible")
elif solution.is_unbounded():
    print("Problema no acotado")
```

---

Para referencia de API completa, ver [README.md](../README.md).