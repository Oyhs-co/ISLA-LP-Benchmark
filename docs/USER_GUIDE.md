# Guía de Usuario - ISLA LP Benchmark

Esta guía es para **usuarios finales** que quieren resolver y comparar problemas de Programación Lineal.

## ¿Qué es Este Proyecto?

ISLA LP Benchmark es una plataforma de benchmarking que permite:
- Resolver problemas de Programación Lineal (PL)
- Comparar múltiples solvers (HiGHS, GLPK, CBC, Gurobi)
- Generar métricas y reportes comparativos

## Inicio Rápido

### 1. Instalar Dependencias

```bash
poetry install
```

### 2. Listar Solvers Disponibles

```bash
python main.py --list-solvers
```

### 3. Resolver un Problema

```bash
python main.py problema.txt
```

### 4. Ejecutar Benchmark

```bash
python main.py --benchmark --solvers highs glpk --repetitions 1 problema.txt
```

## Modo Benchmark

### Ejecución Básica

```bash
# Benchmark con múltiples solvers
python main.py --benchmark --solvers highs glpk cbc --repetitions 3 problema.txt

# Benchmark con gráficos comparativos
python main.py --benchmark --solvers highs glpk --plot-comparison --pdf problema.txt

# Benchmark con visualización
python main.py --benchmark --solvers highs glpk --visualize problema.txt
```

### Flags de Benchmark

| Flag | Descripción |
|------|------------|
| `--benchmark` | Activa modo benchmark |
| `--solvers` | Lista de solvers a usar |
| `--repetitions` | Número de repeticiones |
| `--plot-comparison` | Generar gráficos comparativos |
| `--pdf` | Generar reporte PDF |
| `--output-csv` | Exportar a CSV |
| `--output-dir` | Directorio de salida |

### Ejemplo de Salida

```
============================================================
BENCHMARK SUMMARY
============================================================
Total de pruebas: 6
Exitosas: 6
Fallidas: 0

Por Solver:
------------------------------------------------------------
Solver          Runs     Exitosos   Tiempo Promedio
------------------------------------------------------------
highs           2        2          45.23ms
glpk            2        2          42.87ms
cbc            2        2          48.15ms
============================================================
```

## Solvers Disponibles

| Solver | Paquete | Disponibilidad |
|--------|---------|---------------|
| HiGHS | highspy | ✅ Siempre disponible |
| GLPK | swiglpk | ✅ Siempre disponible |
| CBC | pulp | ✅ Siempre disponible |
| Gurobi | gurobipy | ⚠️ Requiere licencia |
| SCIP | pyscipopt | ⚠️ Requiere instalacion |

**Nota**: SCIP soporta programacion lineal y entera (MILP).

## Resolución Simple

### 1. Crear Archivo de Problema

```lp
max: 3000x + 5000y

2x + 3y <= 120
x + 3y <= 90

x >= 0
y >= 0
```

### 2. Ejecutar

```bash
python main.py problema.txt
```

### 3. Resultados

```
Optimal value: 190000.00
x = 30.00
y = 20.00
```

## Formato de Problemas

### Función Objetivo

```
max: 3000x + 5000y
min: 2x + 3y + 5z
```

### Restricciones

```
x + y <= 100
2x + 3y >= 50
x + y = 75
```

### Límites de Variables

```
x >= 0         # límite inferior
y <= 50        # límite superior
x free         # sin límites
0 <= x <= 100  # ambos límites
```

### Múltiples Problemas

```
max: x + 2y
x + y <= 10
x >= 0; y >= 0

---

min: 3x + y
x - y >= 5
x >= 0; y >= 0
```

## Opciones CLI

### Resolución Simple

| Opción | Descripción |
|--------|-------------|
| `--solver` | Solver a usar (gurobi, highs, glpk, cbc) |
| `--visualize` | Generar gráfico |
| `--pdf` | Generar informe PDF |
| `--verbose` | Salida detallada |
| `--times` | Mostrar tiempos |

### Comandos de Ejemplo

```bash
# Solo resolver
python main.py problema.txt

# Con gráfico
python main.py problema.txt --visualize

# Con informe PDF
python main.py problema.txt --pdf

# Resolver con solver específico
python main.py problema.txt --solver highs

# Todo junto
python main.py problema.txt --visualize --pdf --times
```

## Múltiples Problemas

El sistema soporta resolver múltiples problemas desde un solo archivo usando delimitadores (`---`, `===`, `___`).

### Archivo Multi-Problema
```
max: x + 2y
x + y <= 10
x >= 0; y >= 0

---

min: 3x + y
x - y >= 5
x >= 0; y >= 0
```

### Comandos Multi-Problema
```bash
# Resolver múltiples problemas
python -m src.cli.solve data/problem.txt --multi --solvers gurobi cbc --pdf

# Benchmark de múltiples problemas
python -m src.cli.benchmark data/problem.txt data/milp_example.txt --pdf
```

### Reporte Multi-Problema
El reporte incluye:
1. **Portada** con estadísticas generales
2. **Resumen ejecutivo** con tabla de resultados
3. **Página individual** por problema (función objetivo, restricciones, solución, holguras, gráfico)
4. **Resumen de tiempos** por problema

Referencia: `data/comandos_reportes.md` para más ejemplos.

## MILP (Programación Lineal Entera)

El sistema soporta variables enteras (`int`, `integer`) y binarias (`bin`, `binary`).

### Ejemplo MILP
```
max: 3000x + 5000y

2x + 3y <= 120
x + 3y <= 90

x int          # Variable entera
y binary       # Variable binaria (0 o 1)

x >= 0; y >= 0
```

### Resolver con Gurobi (soporta MILP)
```bash
python -m src.cli.solve data/milp_example.txt --pdf --solver gurobi
```

---

## Entendiendo los Resultados

### Solución Óptima

```
Status: OPTIMAL
Optimal value: 190000.00
x = 30.00
y = 20.00
```

### Problema Infactible

```
Status: INFEASIBLE
```

Significa que las restricciones se contradicen entre sí.

### Problema No Acotado

```
Status: UNBOUNDED
```

El objetivo puede mejorar indefinidamente.

## Reporte PDF Benchmark

El reporte incluye:

1. **Portada**: Información del benchmark
2. **Resumen**: Tabla comparativa por solver
3. **Gráficos**:
   - Tiempo de ejecución
   - Uso de memoria
   - Iteraciones

## Solución de Problemas

### "Solver no disponible"

- Verificar instalación: `python main.py --list-solvers`
- Instalar solver: `pip install highspy` o `pip install swiglpk`

### "Problema infactible"

- Verificar restricciones contradictorias
- Revisar coeficientes

### Resultados incorrectos

- Verificar coefficients
- Verificar direcciones de restricciones

---

Para detalles técnicos, ver [README.md](../README.md).