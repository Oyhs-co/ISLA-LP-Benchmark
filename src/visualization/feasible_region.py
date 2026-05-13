"""
Visualización de región factible para problemas de 2 variables.
Genera gráficos usando matplotlib.
"""

from __future__ import annotations
import math
import tempfile
import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.colors import TABLEAU_COLORS as TAB10_COLORS

from ..core import LinearProblem, LinearConstraint, Solution


class FeasibleRegionVisualization:
    """Visualiza la región factible de un problema de 2 variables."""
    
    def __init__(self, problem: LinearProblem, solution: Solution = None):
        if len(problem.variables) != 2:
            raise ValueError(f"La visualización solo funciona con 2 variables. Tiene {len(problem.variables)}.")
        
        self.problem = problem
        self.solution = solution
        self.var_x = problem.variables[0]
        self.var_y = problem.variables[1]
        self.colors = list(TAB10_COLORS)
    
    def find_intersection(self, c1: LinearConstraint, c2: LinearConstraint) -> tuple:
        a1 = c1.coefficients.get(self.var_x, 0)
        b1 = c1.coefficients.get(self.var_y, 0)
        r1 = c1.rhs
        
        a2 = c2.coefficients.get(self.var_x, 0)
        b2 = c2.coefficients.get(self.var_y, 0)
        r2 = c2.rhs
        
        det = a1 * b2 - a2 * b1
        
        if abs(det) < 1e-10:
            return None
        
        x = (r1 * b2 - r2 * b1) / det
        y = (a1 * r2 - a2 * r1) / det
        
        return (x, y)
    
    def is_point_feasible(self, x, y, constraints) -> bool:
        for c in constraints:
            value = c.coefficients.get(self.var_x, 0) * x + c.coefficients.get(self.var_y, 0) * y
            
            if c.sense == "<=":
                if value > c.rhs + 1e-9:
                    return False
            elif c.sense == ">=":
                if value < c.rhs - 1e-9:
                    return False
            elif c.sense == "=":
                if abs(value - c.rhs) > 1e-9:
                    return False
        return True
    
    def _get_all_constraints_with_bounds(self):
        constraints = list(self.problem.constraints)
        bounds = self.problem.bounds
        
        x_bound = bounds.get(self.var_x)
        y_bound = bounds.get(self.var_y)
        
        if x_bound is None:
            constraints.append(LinearConstraint(coefficients={self.var_x: 1}, rhs=0, sense=">="))
        else:
            if x_bound.lower is not None:
                constraints.append(LinearConstraint(coefficients={self.var_x: 1}, rhs=x_bound.lower, sense=">="))
            if x_bound.upper is not None:
                constraints.append(LinearConstraint(coefficients={self.var_x: 1}, rhs=x_bound.upper, sense="<="))
        
        if y_bound is None:
            constraints.append(LinearConstraint(coefficients={self.var_y: 1}, rhs=0, sense=">="))
        else:
            if y_bound.lower is not None:
                constraints.append(LinearConstraint(coefficients={self.var_y: 1}, rhs=y_bound.lower, sense=">="))
            if y_bound.upper is not None:
                constraints.append(LinearConstraint(coefficients={self.var_y: 1}, rhs=y_bound.upper, sense="<="))
        
        return constraints
    
    def _calculate_plot_range(self, var_x, var_y):
        x_min, x_max = -20, 50
        y_min, y_max = -20, 50
        
        all_constraints = self._get_all_constraints_with_bounds()
        
        for c in all_constraints:
            a = c.coefficients.get(var_x, 0)
            b = c.coefficients.get(var_y, 0)
            rhs = c.rhs
            
            if abs(b) < 1e-10 and abs(a) > 1e-10:
                val = rhs / a
                x_max = max(x_max, abs(val) * 1.5)
                x_min = min(x_min, -abs(val) * 0.5)
            elif abs(a) < 1e-10 and abs(b) > 1e-10:
                val = rhs / b
                y_max = max(y_max, abs(val) * 1.5)
                y_min = min(y_min, -abs(val) * 0.5)
            else:
                if abs(b) > 1e-10:
                    x_intercept = rhs / b
                    x_max = max(x_max, abs(x_intercept) * 1.5)
                    x_min = min(x_min, -abs(x_intercept) * 0.5)
                if abs(a) > 1e-10:
                    y_intercept = rhs / a
                    y_max = max(y_max, abs(y_intercept) * 1.5)
                    y_min = min(y_min, -abs(y_intercept) * 0.5)
        
        if self.solution and self.solution.variables:
            sol_x = self.solution.variables.get(var_x, 0)
            sol_y = self.solution.variables.get(var_y, 0)
            
            x_max = max(x_max, abs(sol_x) + 5)
            y_max = max(y_max, abs(sol_y) + 5)
            x_min = min(x_min, -abs(sol_x) * 0.3 - 2) if sol_x > 0 else min(x_min, sol_x - 2)
            y_min = min(y_min, -abs(sol_y) * 0.3 - 2) if sol_y > 0 else min(y_min, sol_y - 2)
        
        x_range = x_max - x_min
        if x_range < 15:
            center = (x_max + x_min) / 2
            x_min = center - 7.5
            x_max = center + 7.5
        
        y_range = y_max - y_min
        if y_range < 15:
            center = (y_max + y_min) / 2
            y_min = center - 7.5
            y_max = center + 7.5
        
        return x_min, x_max, y_min, y_max
    
    def _find_feasible_vertices(self, constraints):
        vertices = []
        
        for i, c1 in enumerate(constraints):
            for c2 in constraints[i+1:]:
                intersection = self.find_intersection(c1, c2)
                if intersection:
                    x, y = intersection
                    if self.is_point_feasible(x, y, constraints):
                        if not any(math.isclose(x, v[0], abs_tol=1e-8) and 
                                  math.isclose(y, v[1], abs_tol=1e-8) for v in vertices):
                            vertices.append((x, y))
        
        bounds = self.problem.bounds
        
        x_bound = bounds.get(self.var_x)
        y_bound = bounds.get(self.var_y)
        
        x_lower = x_bound.lower if x_bound and x_bound.lower is not None else 0
        y_lower = y_bound.lower if y_bound and y_bound.lower is not None else 0
        
        corner_points = [(x_lower, y_lower)]
        
        for px, py in corner_points:
            if self.is_point_feasible(px, py, constraints):
                if not any(math.isclose(px, v[0], abs_tol=1e-8) and 
                          math.isclose(py, v[1], abs_tol=1e-8) for v in vertices):
                    vertices.append((px, py))
        
        return vertices
    
    def plot_to_tempfile(self) -> str:
        """Genera el gráfico y lo guarda en un archivo temporal. Retorna la ruta."""
        var_x = self.var_x
        var_y = self.var_y
        x_min, x_max, y_min, y_max = self._calculate_plot_range(var_x, var_y)
        
        fig, ax = plt.subplots(figsize=(7, 5.5))
        
        colors = list(TAB10_COLORS)
        x_vals = np.linspace(x_min, x_max, 200)
        
        all_constraints = self._get_all_constraints_with_bounds()
        
        for i, c in enumerate(self.problem.constraints):
            a = c.coefficients.get(var_x, 0)
            b = c.coefficients.get(var_y, 0)
            rhs = c.rhs
            
            label = f"R{i+1}"
            
            if abs(b) < 1e-10 and abs(a) > 1e-10:
                x_const = rhs / a
                y_range = np.linspace(y_min, y_max, 200)
                x_line = np.full_like(y_range, x_const)
                linestyle = '--' if c.sense == ">=" else ('-' if c.sense == "<=" else ':')
                ax.plot(x_line, y_range, color=colors[i % len(colors)], 
                        linewidth=2, linestyle=linestyle, label=label)
            else:
                y_vals = (rhs - a * x_vals) / b
                valid = np.isfinite(y_vals)
                linestyle = '--' if c.sense == ">=" else ('-' if c.sense == "<=" else ':')
                ax.plot(x_vals[valid], y_vals[valid], color=colors[i % len(colors)], 
                        linewidth=2, linestyle=linestyle, label=label)
        
        vertices = self._find_feasible_vertices(all_constraints)
        
        if len(vertices) >= 3:
            cx = sum(v[0] for v in vertices) / len(vertices)
            cy = sum(v[1] for v in vertices) / len(vertices)
            vertices_sorted = sorted(vertices, key=lambda v: math.atan2(v[1] - cy, v[0] - cx))
            
            polygon = Polygon(vertices_sorted, closed=True, alpha=0.3, 
                             facecolor='#90EE90', edgecolor='#228B22', linewidth=2)
            ax.add_patch(polygon)
        elif len(vertices) == 2:
            ax.fill([v[0] for v in vertices] + [vertices[0][0]], 
                   [v[1] for v in vertices] + [vertices[0][1]], 
                   alpha=0.3, facecolor='#90EE90', edgecolor='#228B22', linewidth=2)
        
        for i, c in enumerate(all_constraints):
            if c not in self.problem.constraints:
                a = c.coefficients.get(var_x, 0)
                b = c.coefficients.get(var_y, 0)
                rhs = c.rhs
                
                if abs(b) < 1e-10 and abs(a) > 1e-10:
                    x_const = rhs / a
                    y_range = np.linspace(y_min, y_max, 200)
                    x_line = np.full_like(y_range, x_const)
                    linestyle = '--' if c.sense == ">=" else ('-' if c.sense == "<=" else ':')
                    ax.plot(x_line, y_range, color='gray', linewidth=1.5, 
                           linestyle=linestyle, alpha=0.6)
                elif abs(a) < 1e-10 and abs(b) > 1e-10:
                    y_const = rhs / b
                    ax.axhline(y_const, color='gray', linewidth=1.5, 
                               linestyle=linestyle, alpha=0.6)
        
        if self.solution and self.solution.variables:
            x = self.solution.variables.get(var_x, 0)
            y = self.solution.variables.get(var_y, 0)
            ax.scatter([x], [y], color='red', s=300, zorder=10, marker='*', 
                      edgecolors='black', linewidths=1.5)
            ax.annotate(f'Optimo\n({x:.2f}, {y:.2f})', (x, y), 
                       textcoords="offset points", xytext=(15, 15), fontsize=10,
                       fontweight='bold', color='darkred',
                       arrowprops=dict(arrowstyle='->', color='darkred', lw=1.5))
            
            obj = self.problem.objective
            a = obj.get(var_x, 0)
            b = obj.get(var_y, 0)
            
            if abs(b) > 1e-10:
                opt_val = a * x + b * y
                y_obj = (opt_val - a * x_vals) / b
                valid = np.isfinite(y_obj) & (y_obj >= y_min) & (y_obj <= y_max)
                ax.plot(x_vals[valid], y_obj[valid], 'b--', alpha=0.6, linewidth=1.5,
                       label=f'Funcion objetivo (Z={opt_val:.2f})')
        
        padding_x = (x_max - x_min) * 0.1
        padding_y = (y_max - y_min) * 0.1
        ax.set_xlim(x_min - padding_x, x_max + padding_x)
        ax.set_ylim(y_min - padding_y, y_max + padding_y)
        
        ax.set_xlabel(var_x, fontsize=12, fontweight='bold')
        ax.set_ylabel(var_y, fontsize=12, fontweight='bold')
        ax.set_title(f'Region Factible - {self.problem.sense.upper()}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.axhline(y=0, color='black', linewidth=1)
        ax.axvline(x=0, color='black', linewidth=1)
        ax.legend(loc='upper right', fontsize=8, framealpha=0.9)
        
        tmp_path = None
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            plt.savefig(tmp.name, dpi=150, bbox_inches='tight', facecolor='white')
            tmp_path = tmp.name
        
        plt.close()
        return tmp_path
