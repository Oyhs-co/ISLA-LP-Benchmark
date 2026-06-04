"""
Router: carga y parseo de problemas LP/MPS.
"""
import uuid
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, Request, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.parser import LPParser, MPSParser
from src.solver import SolverRegistry
from src.web.state import store

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")
templates.env.filters["enumerate"] = enumerate


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    solvers = SolverRegistry.list_solvers(available_only=True)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"solvers": solvers},
    )


@router.post("/upload", response_class=HTMLResponse)
async def upload(
    request: Request,
    file: Optional[UploadFile] = None,
    text: str = Form(""),
):
    if file and file.filename:
        content = (await file.read()).decode("utf-8")
    elif text.strip():
        content = text
    else:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request, "message": "No se proporcionó ningún problema."},
        )

    try:
        is_mps = content.strip().upper().startswith(("NAME", "ROWS"))
        problem = MPSParser(content).parse() if is_mps else LPParser(content).parse()
        pid = str(uuid.uuid4())
        store.save_problem(pid, problem)
        return templates.TemplateResponse(            
            request=request,
            name="problem_detail.html",
            context={
                "request": request,
                "problem": problem,
                "pid": pid,
                "solvers": SolverRegistry.list_solvers(available_only=True),
            },
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request, "message": f"Error al parsear: {exc}"},
        )


@router.post("/load-example", response_class=HTMLResponse)
async def load_example(request: Request, example: str = Form("simple")):
    from src.utils.problem_generator import ProblemGenerator

    gen = ProblemGenerator(random_state=42)
    if example == "mip":
        problem = gen.generate_milp(n_vars=4, n_constraints=6, n_int_vars=2)
    elif example == "netlib":
        problem = gen.generate_netlib_like("afiro")
    else:
        problem = gen.generate_lp(n_vars=3, n_constraints=4)

    pid = str(uuid.uuid4())
    store.save_problem(pid, problem)
    return templates.TemplateResponse(
        request=request,
        name="problem_detail.html",
        context={
            "request": request,
            "problem": problem,
            "pid": pid,
            "solvers": SolverRegistry.list_solvers(available_only=True),
        },
    )