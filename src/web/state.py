"""
Estado compartido en memoria para problemas y soluciones.
En producción reemplazar por Redis u otro backend.
"""
from src.core import LinearProblem


class InMemoryStore:
    def __init__(self):
        self._problems: dict[str, LinearProblem] = {}
        self._solutions: dict[str, dict] = {}

    # --- Problemas ---
    def save_problem(self, pid: str, problem: LinearProblem) -> None:
        self._problems[pid] = problem

    def get_problem(self, pid: str) -> LinearProblem | None:
        return self._problems.get(pid)

    # --- Soluciones ---
    def save_solution(self, sol_id: str, data: dict) -> None:
        self._solutions[sol_id] = data

    def get_solution(self, sol_id: str) -> dict | None:
        return self._solutions.get(sol_id)


store = InMemoryStore()