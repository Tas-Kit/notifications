import pytest
from src import create_app


@pytest.fixture
def app():
    app = create_app()
    return app

myapp = create_app()
