import python_template


def test_package_imports() -> None:
    """The package is importable under its public name."""
    assert python_template.__name__ == "python_template"
