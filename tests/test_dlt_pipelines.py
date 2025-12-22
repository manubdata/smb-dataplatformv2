def test_project_structure():
    """Simple test to verify environment is working"""
    assert 1 + 1 == 2


def test_dlt_import():
    """Verify dlt is installed and accessible"""
    import dlt

    assert dlt is not None