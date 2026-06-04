"""
Router: resolución de problemas LP/MPS.
"""
import time
import uuid
from pathlib import Path

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.solver import SolverConfig, SolverRegistry
from src.web.state import store

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")
templates.env.filters["enumerate"] = enumerate



@router.post("/solve/{pid}", response_class=HTMLResponse)
async def solve(
    request: Request,
    pid: str,
    solver: str = Form(...),
    time_limit: float = Form(300.0),
):
    problem = store.get_problem(pid)
    if problem is None:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request, "message": "Problema no encontrado."},
        )

    solver_class = SolverRegistry.get(solver)
    if solver_class is None:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request, "message": f"Solver '{solver}' no disponible."},
        )

    try:
        config = SolverConfig(time_limit=time_limit if time_limit > 0 else None)
        instance = solver_class(problem, config)

        start = time.perf_counter()
        solution = instance.solve()
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        sol_id = str(uuid.uuid4())
        store.save_solution(
            sol_id,
            {
                "solver": solver,
                "status": solution.status,
                "objective_value": solution.objective_value,
                "variables": solution.variables,
                "time_ms": elapsed_ms,
                "numerical_quality": solution.numerical_quality,
            },
        )

        return templates.TemplateResponse(
            request=request,
            name="solution.html",
            context={
                "request": request,
                "solver": solver,
                "solution": solution,
                "elapsed_ms": elapsed_ms,
            },
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request, "message": f"Error al resolver: {exc}"},
        )