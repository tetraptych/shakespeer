"""Test imports used in main.py."""


def test_all_imports():
    """
    Test all imports.

    Used to ensure all files are included during test coverage calculation
    """
    from shakespeer.app import main
    dir(main)
