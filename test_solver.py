from src.parser import LPParser
from src.matrix import LPBuilder
from src.solver import SolverLP

problem_text = """
max u = 3x + 5y - 2z

# restricciones
2x + y <= 18
2x + 3y >= 10
x + y = 5

# bounds
x >= 0
y <= 10
z free
"""

problem = LPParser(problem_text).parse()
lp = LPBuilder(problem).build()

SolverLP(problem).solve()
