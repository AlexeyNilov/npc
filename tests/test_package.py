import npc


def test_package_imports() -> None:
    """The package is importable under its public name."""
    assert npc.__name__ == "npc"
