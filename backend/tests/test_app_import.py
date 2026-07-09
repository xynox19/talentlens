import importlib


def test_backend_app_imports_as_package():
    module = importlib.import_module("backend.app")

    assert module.app is not None
    assert module.app.name == "backend.app"
