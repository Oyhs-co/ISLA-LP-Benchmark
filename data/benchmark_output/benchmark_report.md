# Reporte de Benchmarking

Fecha: 2026-05-17 07:27:08

## Resumen
- Total de pruebas: 100
- Exitosas: 100
- Fallidas: 0

## Por Solver

| Solver | Pruebas | Exitosas | Tiempo Promedio |
|--------|---------|----------|-----------------|
| gurobi | 10 | 10 | 88.41ms |
| highs | 10 | 10 | 85.84ms |
| glpk | 10 | 10 | 84.67ms |
| cbc | 10 | 10 | 218.25ms |
| scip | 10 | 10 | 106.96ms |
| ecos | 10 | 10 | 85.33ms |
| osqp | 10 | 10 | 98.50ms |
| cvxopt | 10 | 10 | 103.25ms |
| scs | 10 | 10 | 77.30ms |
| ipopt | 10 | 10 | 335.27ms |

## Detalle de Resultados

| Problema | Solver | Estado | Valor Obj. | Tiempo |
|----------|--------|--------|------------|--------|
| Problema_1 | gurobi | OK | 8.00 | 88.05ms |
| Problema_1 | highs | OK | 8.00 | 107.81ms |
| Problema_1 | glpk | OK | 8.00 | 89.97ms |
| Problema_1 | cbc | OK | 8.00 | 399.34ms |
| Problema_1 | scip | OK | 8.00 | 199.13ms |
| Problema_1 | ecos | OK | 11.43 | 105.71ms |
| Problema_1 | osqp | OK | 11.43 | 77.48ms |
| Problema_1 | cvxopt | OK | 11.43 | 253.76ms |
| Problema_1 | scs | OK | 11.43 | 73.96ms |
| Problema_1 | ipopt | OK | 8.00 | 2272.22ms |
| Problema_2 | gurobi | OK | 406.67 | 87.33ms |
| Problema_2 | highs | OK | 406.67 | 89.16ms |
| Problema_2 | glpk | OK | 406.67 | 73.27ms |
| Problema_2 | cbc | OK | 406.67 | 138.73ms |
| Problema_2 | scip | OK | 406.67 | 105.43ms |
| Problema_2 | ecos | OK | 406.67 | 80.09ms |
| Problema_2 | osqp | OK | 406.67 | 149.61ms |
| Problema_2 | cvxopt | OK | 406.67 | 91.59ms |
| Problema_2 | scs | OK | 406.67 | 90.16ms |
| Problema_2 | ipopt | OK | 406.67 | 96.36ms |
| Problema_3 | gurobi | OK | 68.00 | 76.34ms |
| Problema_3 | highs | OK | 68.00 | 70.71ms |
| Problema_3 | glpk | OK | 68.00 | 83.58ms |
| Problema_3 | cbc | OK | 68.00 | 151.35ms |
| Problema_3 | scip | OK | 68.00 | 88.51ms |
| Problema_3 | ecos | OK | 68.00 | 113.26ms |
| Problema_3 | osqp | OK | 68.00 | 183.45ms |
| Problema_3 | cvxopt | OK | 68.00 | 81.30ms |
| Problema_3 | scs | OK | 68.00 | 68.37ms |
| Problema_3 | ipopt | OK | 68.00 | 99.27ms |
| Problema_4 | gurobi | OK | 1253.33 | 82.07ms |
| Problema_4 | highs | OK | 1253.33 | 79.47ms |
| Problema_4 | glpk | OK | 1253.33 | 83.25ms |
| Problema_4 | cbc | OK | 1253.33 | 173.35ms |
| Problema_4 | scip | OK | 1253.33 | 106.36ms |
| Problema_4 | ecos | OK | 1253.33 | 87.77ms |
| Problema_4 | osqp | OK | 1253.33 | 90.33ms |
| Problema_4 | cvxopt | OK | 1253.33 | 81.54ms |
| Problema_4 | scs | OK | 1253.40 | 70.25ms |
| Problema_4 | ipopt | OK | 1253.33 | 123.00ms |
| Problema_5 | gurobi | OK | 80.00 | 82.36ms |
| Problema_5 | highs | OK | 80.00 | 69.54ms |
| Problema_5 | glpk | OK | 80.00 | 89.38ms |
| Problema_5 | cbc | OK | 80.00 | 159.82ms |
| Problema_5 | scip | OK | 80.00 | 116.12ms |
| Problema_5 | ecos | OK | 80.00 | 90.83ms |
| Problema_5 | osqp | OK | 80.00 | 81.33ms |
| Problema_5 | cvxopt | OK | 80.00 | 84.68ms |
| Problema_5 | scs | OK | 80.00 | 71.42ms |
| Problema_5 | ipopt | OK | 80.00 | 115.80ms |
| Problema_6 | gurobi | OK | 18233.33 | 78.39ms |
| Problema_6 | highs | OK | 18233.33 | 88.59ms |
| Problema_6 | glpk | OK | 18233.33 | 79.38ms |
| Problema_6 | cbc | OK | 18233.33 | 218.54ms |
| Problema_6 | scip | OK | 18233.33 | 91.93ms |
| Problema_6 | ecos | OK | 18233.33 | 70.97ms |
| Problema_6 | osqp | OK | 18233.33 | 78.59ms |
| Problema_6 | cvxopt | OK | 18233.33 | 82.71ms |
| Problema_6 | scs | OK | 18233.33 | 71.68ms |
| Problema_6 | ipopt | OK | 18233.33 | 110.64ms |
| Problema_7 | gurobi | OK | 403.08 | 88.60ms |
| Problema_7 | highs | OK | 403.08 | 83.89ms |
| Problema_7 | glpk | OK | 403.08 | 81.97ms |
| Problema_7 | cbc | OK | 403.08 | 338.99ms |
| Problema_7 | scip | OK | 403.08 | 90.93ms |
| Problema_7 | ecos | OK | 403.08 | 76.84ms |
| Problema_7 | osqp | OK | 403.08 | 80.62ms |
| Problema_7 | cvxopt | OK | 403.08 | 84.64ms |
| Problema_7 | scs | OK | 403.08 | 79.67ms |
| Problema_7 | ipopt | OK | 403.08 | 116.73ms |
| Problema_8 | gurobi | OK | 1020.00 | 87.65ms |
| Problema_8 | highs | OK | 1020.00 | 98.88ms |
| Problema_8 | glpk | OK | 1020.00 | 96.07ms |
| Problema_8 | cbc | OK | 1020.00 | 219.92ms |
| Problema_8 | scip | OK | 1020.00 | 83.43ms |
| Problema_8 | ecos | OK | 1020.00 | 75.01ms |
| Problema_8 | osqp | OK | 1020.00 | 78.21ms |
| Problema_8 | cvxopt | OK | 1020.00 | 84.73ms |
| Problema_8 | scs | OK | 1020.01 | 83.15ms |
| Problema_8 | ipopt | OK | 1020.00 | 102.88ms |
| Problema_9 | gurobi | OK | 71730.77 | 112.34ms |
| Problema_9 | highs | OK | 71730.77 | 91.08ms |
| Problema_9 | glpk | OK | 71730.77 | 88.64ms |
| Problema_9 | cbc | OK | 71730.77 | 145.42ms |
| Problema_9 | scip | OK | 71730.77 | 90.95ms |
| Problema_9 | ecos | OK | 71730.77 | 73.90ms |
| Problema_9 | osqp | OK | 71730.77 | 87.36ms |
| Problema_9 | cvxopt | OK | 71730.77 | 93.51ms |
| Problema_9 | scs | OK | 71731.37 | 72.36ms |
| Problema_9 | ipopt | OK | 71730.77 | 144.46ms |
| Problema_10 | gurobi | OK | 7790.00 | 100.96ms |
| Problema_10 | highs | OK | 7790.00 | 79.26ms |
| Problema_10 | glpk | OK | 7790.00 | 81.22ms |
| Problema_10 | cbc | OK | 7790.00 | 237.05ms |
| Problema_10 | scip | OK | 7790.00 | 96.76ms |
| Problema_10 | ecos | OK | 7790.00 | 78.95ms |
| Problema_10 | osqp | OK | 7790.00 | 78.00ms |
| Problema_10 | cvxopt | OK | 7790.00 | 94.01ms |
| Problema_10 | scs | OK | 5256.92 | 91.98ms |
| Problema_10 | ipopt | OK | 7790.00 | 171.30ms |