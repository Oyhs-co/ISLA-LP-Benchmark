# Guía de Contribución - Gurobipy-Simplex-General-Solver

¡Gracias por tu interés en contribuir!

Este documento proporciona lineamientos para contribuir a este proyecto.

## Inicio Rápido

1. Hacer fork del repositorio
2. Crear una rama de funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Hacer los cambios
4. Verificar funcionalidad
5. Hacer commit (`git commit -am 'Agregar nueva funcionalidad'`)
6. Push a la rama (`git push origin feature/nueva-funcionalidad`)
7. Crear un Pull Request

## Configuración de Desarrollo

```bash
# Clonar repositorio
git clone <url-del-fork>
cd gurobipy-simplex-general-solver

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install poetry
poetry install

# Instalar pre-commit hooks (opcional)
pre-commit install
```

## Estándares de Código

- **Lenguaje**: Python 3.12+
- **Docstrings**: Español (estándar del proyecto)
- **Type hints**: Requerido para código nuevo
- **Formato**: Seguir estilo existente

## Estilo de Código

```python
# Usar dataclasses para estructuras simples
@dataclass
class MiClase:
    atributo: str
    valor: int = 0

# Usar type hints
def mi_funcion(param: str) -> int:
    return len(param)

# Documentar en español
def mi_funcion(param: str) -> int:
    """
    Descripción de la función.

    Args:
        param: Descripción del parámetro.

    Returns:
        Descripción del valor de retorno.
    """
    pass
```

## Verificación

Antes de enviar, verificar:

```bash
# Ejecutar test básico
python main.py data/problem.txt
python main.py data/problem_multi.txt --multi
```

## Enviando Cambios

1. Asegurar que todo funcione
2. Actualizar documentación si es necesario
3. Agregar mensaje de commit claro
4. Crear un Pull Request

## Reportando Problemas

Al reportar problemas:

1. Verificar que no haya sido reportado
2. Proporcionar pasos de reproducción
3. Incluir info del entorno (OS, Python, dependencias)
4. Adjuntar archivos de prueba si es posible

## Licencia

Al contribuir, aceptas que tus contribuciones estarán bajo la Licencia MIT.