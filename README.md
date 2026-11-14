# Inventario TI

![CI](https://github.com/AlecCastroA/inventario-ti-qa/actions/workflows/ci.yml/badge.svg)

API REST para controlar el inventario de equipos de TI de una oficina pequeña. Esta versión extiende el proyecto del PA1 con una estrategia de aseguramiento de calidad: pruebas automatizadas, cobertura en el pipeline, gestión de defectos y métricas.

## Funcionalidades

- Registrar un equipo (tipo, marca/modelo, número de serie único).
- Listar equipos y filtrar por tipo, estado o texto.
- Consultar el detalle de un equipo por ID.
- Asignar, devolver y dar de baja un equipo.
- Consultar el historial de movimientos de un equipo.
- Consultar el estado de la API y el entorno activo.

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/equipos` | Registra un equipo |
| GET | `/equipos` | Lista equipos (filtros opcionales `tipo`, `estado` y `q`) |
| GET | `/equipos/{id}` | Detalle de un equipo |
| POST | `/equipos/{id}/asignar` | Asigna el equipo a un usuario |
| POST | `/equipos/{id}/devolver` | Devuelve un equipo asignado |
| POST | `/equipos/{id}/baja` | Da de baja el equipo |
| GET | `/equipos/{id}/historial` | Movimientos del equipo |
| GET | `/salud` | Estado de la API y entorno activo |

La documentación interactiva está en `/docs` cuando la API está en ejecución.

## Tecnología

Python 3.12, FastAPI, pytest, pytest-cov, ruff y GitHub Actions. Los datos se guardan en memoria.

## Instalación

```bash
git clone https://github.com/AlecCastroA/inventario-ti-qa.git
cd inventario-ti-qa
python -m venv .venv
source .venv/Scripts/activate   # Git Bash en Windows; en Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecución

```bash
bash scripts/ejecutar.sh desarrollo    # con recarga automática
bash scripts/ejecutar.sh produccion    # sin recarga
```

O manualmente, con el entorno virtual activo: `uvicorn app.main:app --reload`. La API queda en `http://127.0.0.1:8000`.

## Pruebas y cobertura

```bash
pytest                                        # todas las pruebas
pytest --cov=app --cov-report=term-missing    # con reporte de cobertura
ruff check .                                  # lint
```

El pipeline ejecuta estas verificaciones en cada push a `develop` o `main` y en cada Pull Request, exige una cobertura mínima de 80 % y bloquea el merge si algo falla.

## Estrategia de calidad

- `tests/test_equipos.py`: pruebas funcionales de cada endpoint.
- `tests/test_caja_negra.py`: valores límite, particiones de equivalencia y adivinanza de errores.
- `tests/test_caja_blanca.py`: pruebas del servicio que cubren decisiones y ramas.
- Los defectos encontrados se registran en GitHub Issues con descripción, pasos para reproducirlos, severidad y estado.

## Estructura del proyecto

```
app/          código de la API
tests/        pruebas automatizadas
docs/         diagramas y guías técnicas
scripts/      script de ejecución por entorno
.github/      workflow de integración continua
```

Más información en [arquitectura](docs/arquitectura.md) y [despliegue](docs/despliegue.md).

## Flujo de trabajo

- Ramas: `main` (estable), `develop` (integración), `feature/*` y `test/*`. Todo cambio entra a `develop` mediante Pull Request con revisión.
- Commits siguiendo [Conventional Commits](https://www.conventionalcommits.org/es/).

## Limitaciones conocidas

- Los datos se pierden al reiniciar la API.
- No hay autenticación ni despliegue público.