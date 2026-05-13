"""
Modulo de CLI para el solver de programacion lineal.
Maneja la interfaz de linea de comandos.
"""

import argparse
import sys
from pathlib import Path

from src.cli import solve, benchmark
from src.cli import get_system_info


def create_parser() -> argparse.ArgumentParser:
    """Crea el parser de argumentos."""
    parser = argparse.ArgumentParser(
        prog='lp-solver',
        description='Solucionador de Programacion Lineal con Gurobi',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s problema.txt                    Resolver un problema
  %(prog)s problema.txt --visualize         Resolver y graficar
  %(prog)s problema.txt --pdf               Generar reporte PDF
  %(prog)s --benchmark problemas.txt      Modo benchmark
        """
    )
    
    parser.add_argument(
        'input',
        nargs='?',
        help='Archivo con el problema de PL'
    )
    
    parser.add_argument(
        '--solver', '-s',
        type=str,
        default='gurobi',
        help='Solver a usar (default: gurobi)'
    )
    
    parser.add_argument(
        '--multi', '-m',
        action='store_true',
        help='Modo multi-problema (separados por ---)'
    )
    
    parser.add_argument(
        '--visualize', '-v',
        action='store_true',
        help='Generar grafica de region factible'
    )
    
    parser.add_argument(
        '--pdf', '-p',
        action='store_true',
        help='Generar reporte PDF'
    )
    
    parser.add_argument(
        '--times', '-t',
        action='store_true',
        help='Mostrar tiempos de ejecucion'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Salida detallada'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Ruta de salida para archivos generados'
    )
    
    parser.add_argument(
        '--benchmark', '-b',
        action='store_true',
        help='Ejecutar en modo benchmark'
    )
    
    parser.add_argument(
        '--solvers',
        nargs='+',
        default=['gurobi'],
        help='Solvers a usar en benchmark'
    )
    
    parser.add_argument(
        '--repetitions', '-r',
        type=int,
        default=1,
        help='Numero de repeticiones para benchmark'
    )
    
    parser.add_argument(
        '--output-csv',
        type=str,
        help='Exportar resultados a CSV'
    )
    
    parser.add_argument(
        '--plot-comparison',
        action='store_true',
        help='Generar graficos comparativos'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Directorio de salida para resultados'
    )
    
    parser.add_argument(
        '--list-solvers',
        action='store_true',
        help='Listar solvers disponibles'
    )
    
    return parser


def main(argv: list[str] = None) -> int:
    """Punto de entrada principal."""
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if args.list_solvers:
        from src.solver import SolverRegistry
        print("=== Solvers Disponibles ===")
        print()
        all_info = SolverRegistry.list_all_info()
        for name, info in all_info.items():
            status = "DISPONIBLE" if info['available'] else "NO DISPONIBLE"
            print(f"  {name}: {status}", end='')
            if info['error']:
                print(f" - {info['error']}")
            else:
                print()
        print()
        print("Available only:", SolverRegistry.list_solvers(available_only=True))
        return 0
    
    solver_name = args.solver
    
    if args.benchmark:
        return benchmark.run_benchmark(
            input_path=Path(args.input) if args.input else None,
            solvers=args.solvers if args.solvers else ['gurobi'],
            repetitions=args.repetitions,
            visualize=args.plot_comparison,
            output_csv=args.output_csv,
            plot_comparison=args.plot_comparison,
            output_dir=args.output_dir if args.output_dir else None,
            verbose=args.verbose,
            pdf=args.pdf
        )
    
    if args.input:
        if args.multi:
            return solve.solve_multi(
                Path(args.input),
                solver_name=solver_name,
                visualize=args.visualize,
                pdf=args.pdf,
                times=args.times,
                verbose=args.verbose,
                output=args.output
            )
        else:
            return solve.solve_single(
                Path(args.input),
                solver_name=solver_name,
                visualize=args.visualize,
                pdf=args.pdf,
                times=args.times,
                verbose=args.verbose,
                output=args.output
            )
    
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
