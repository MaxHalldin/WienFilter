def test_main() -> None:
    from pythion import MainWindowComponent
    assert MainWindowComponent._instance is None
    print(MainWindowComponent)
