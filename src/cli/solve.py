"""
Handler para resolver problemas individuales de programacion lineal.
"""

import time
from pathlib import Path
from typing import Optional

from src.parser import LPParser
from src.matrix import LPBuilder
from src.solver import SolverLP, SolverConfig, SolverRegistry
from src.visualization import LinearVisualization
from src.analysis import LPAnalysis, ExecutionTimes
from src.cli import get_system_info


def solve_single(
    input_path: Path,
    solver_name: str = "highs",
    visualize: bool = False,
    pdf: bool = False,
    times: bool = False,
    verbose: bool = False,
    output: Optional[str] = None
) -> int:
    """Resuelve un problema individual."""
    if not input_path.exists():
        print(f"Error: Archivo no encontrado: {input_path}")
        return 1
    
    start_total = time.perf_counter()
    
    try:
        solver_class = SolverRegistry.get(solver_name)
        if solver_class is None:
            print(f"Error: Solver '{solver_name}' no encontrado")
            return 1
        
        with open(input_path, 'r') as f:
            problem_text = f.read()
        
        start_parse = time.perf_counter()
        problem = LPParser(problem_text).parse()
        parse_time = time.perf_counter() - start_parse
        
        start_build = time.perf_counter()
        lp = LPBuilder(problem).build()
        build_time = time.perf_counter() - start_build
        
        config = SolverConfig(verbose=verbose)
        start_solve = time.perf_counter()
        # Pass LinearProblem to solver
        try:
            solver = solver_class(problem, config)
        except TypeError:
            # Fallback for solvers that only accept problem
            solver = solver_class(problem)
            solver.config = config
        solution = solver.solve()
        solve_time = time.perf_counter() - start_solve
        
        if solution.is_optimal():
            print(f"Optimal value: {solution.objective_value:.2f}")
            for var, value in solution.variables.items():
                print(f"{var} = {value:.2f}")
        else:
            print(f"Status: {solution.status}")
        
        if visualize and len(problem.variables) == 2:
            print("\nGenerating visualization...")
            output_path = output or input_path.with_suffix('.png')
            viz = LinearVisualization(problem, solution)
            viz.plot(save_path=str(output_path), show=False)
            print(f"Graph saved to: {output_path}")
        
        if pdf:
            from src.analysis import LPAnalysis, ExecutionTimes
            from src.cli import get_system_info
            print("\nGenerating PDF report...")
            exec_times = ExecutionTimes(
                parse_time=parse_time,
                build_time=build_time,
                solve_time=solve_time,
                total_time=time.perf_counter() - start_total
            )
            output_path = output or input_path.with_suffix('.pdf')
            system_info = get_system_info()
            analysis = LPAnalysis(problem, solution, exec_times, system_info, solver_name)
            analysis.generate_pdf(str(output_path))
            print(f"PDF saved to: {output_path}")
        
        if times:
            total_time = time.perf_counter() - start_total
            print("\n" + "="*50)
            print("EXECUTION TIMES")
            print("="*50)
            print(f"Parsing:           {parse_time*1000:.6f} ms")
            print(f"Building LP:       {build_time*1000:.6f} ms")
            print(f"Solving ({solver_name}): {solve_time*1000:.6f} ms")
            print("-"*50)
            print(f"TOTAL:             {total_time*1000:.6f} ms")
            print("="*50)
            print(f"Parsing:           {parse_time*1000:.6f} ms")
            print(f"Building LP:       {build_time*1000:.6f} ms")
            print(f"Solving ({solver_name}): {solve_time*1000:.6f} ms")
            print("-"*50)
            print(f"TOTAL:             {total_time*1000:.6f} ms")
            print("="*50)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


def solve_multi(
    input_path: Path,
    solver_name: str = "highs",
    visualize: bool = False,
    pdf: bool = False,
    times: bool = False,
    verbose: bool = False,
    output: Optional[str] = None
) -> int:
    """Resuelve multiples problemas."""
    if not input_path.exists():
        print(f"Error: Archivo no encontrado: {input_path}")
        return 1
    
    try:
        solver_class = SolverRegistry.get(solver_name)
        if solver_class is None:
            print(f"Error: Solver '{solver_name}' no encontrado")
            return 1
        
        with open(input_path, 'r') as f:
            content = f.read()
        
        from src.parser import MultiLPParser
        parser = MultiLPParser(content)
        problems = parser.parse_all()
        
        print(f"\n{'='*50}")
        print("MULTI-PROBLEM MODE")
        print("="*50)
        print(f"Problems found: {len(problems)}")
        print(f"Solver: {solver_name}")
        
        print("\nSolving problems...\n")
        
        results = []
        for i, problem in enumerate(problems, 1):
            print(f"--- Problema {i} ---")
            
            import time
            start = time.perf_counter()
            
            try:
                solver = solver_class(problem)
                solution = solver.solve()
                solve_time = time.perf_counter() - start
            except Exception as e:
                print(f"Error: {e}")
                continue
            
            # Guardar resultado
            from src.solver import ProblemResult
            result = ProblemResult(
                problem=problem,
                solution=solution,
                solve_time=solve_time
            )
            results.append(result)
            
            if solution.is_optimal():
                print(f"Status: OPTIMAL")
                print(f"Optimal value: {solution.objective_value:.4f}")
                vars_str = ", ".join(f"{k}={v:.2f}" for k, v in solution.variables.items())
                print(f"Variables: {vars_str}")
            else:
                print(f"Status: {solution.status}")
            
            if visualize and len(problem.variables) == 2:
                from src.visualization import LinearVisualization
                output_name = f"{input_path.stem}_problema_{i}.png"
                viz = LinearVisualization(problem, solution)
                viz.plot(save_path=output_name, show=False)
                print(f"Graph saved to: {output_name}")
        
        print(f"\nProblems solved: {len(results)}/{len(problems)}")
        
        # Generar PDF si se solicita
        if pdf and results:
            print("\nGenerando reporte PDF multi-problema...")
            try:
                from src.analysis.multi_analysis import MultiLPAnalysis
                from src.solver import MultiSolverResult
                from pathlib import Path
                
                output_path = Path(output or input_path.with_stem(input_path.stem + "_multi").with_suffix('.pdf'))
                
                # Crear MultiSolverResult
                multi_result = MultiSolverResult(
                    results=results,
                    solver_name=solver_name
                )
                
                analysis = MultiLPAnalysis(multi_result)
                analysis.generate_pdf(str(output_path))
                print(f"PDF multi-problema guardado en: {output_path}")
            except Exception as e:
                print(f"Error generando PDF multi: {e}")
                if verbose:
                    import traceback
                    traceback.print_exc()
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return 1
