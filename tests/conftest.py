import pytest
from fastapi.testclient import TestClient

from app.main import app, get_service
from app.repository import EquipoRepository
from app.service import EquipoService


@pytest.fixture
def client():
    repositorio = EquipoRepository()
    app.dependency_overrides[get_service] = lambda: EquipoService(repositorio)
    yield TestClient(app)
    app.dependency_overrides.clear()