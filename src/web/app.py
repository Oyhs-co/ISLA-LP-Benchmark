"""
Aplicacion web FastAPI + HTMX para resolver problemas de PL.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.web.routes import problems, solver
from src.web.state import store   # store compartido entre routers

def create_app() -> FastAPI:
    app = FastAPI(title="ISLA LP Solver Web", version="1.8.1")

    # Montaje de archivos estáticos (CSS, JS propios si los hubiera)
    # app.mount("/static", StaticFiles(directory="static"), name="static")

    # Registrar routers
    app.include_router(problems.router)
    app.include_router(solver.router)

    return app


app = create_app()