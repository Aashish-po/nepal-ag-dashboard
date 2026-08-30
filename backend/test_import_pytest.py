def test_districts_router_import():
    """Test that we can import the districts router."""
    from api.routes.districts import router as districts_router

    print(f"Imported router from: {districts_router.__module__}")
    # Try to get the module file if possible
    try:
        import api.routes.districts as districts_module

        print(f"Module file: {districts_module.__file__}")
    except AttributeError as e:
        print(f"Could not get module file: {e}")
    assert districts_router is not None
