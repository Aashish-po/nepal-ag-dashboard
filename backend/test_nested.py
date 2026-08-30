"""Minimal test to reproduce the FastAPI dependency issue."""

from typing import Annotated

from fastapi import Depends, FastAPI, Query


# Mock classes for testing
class MockSession:
    pass


class SimpleValidator:
    def __init__(self, session: MockSession):
        self.session = session

    def validate_province(self, province):
        return True

    def validate_region(self, region):
        return True


def get_session():
    """Mock dependency function that yields a session."""
    yield MockSession()


def get_validator(session: Annotated[MockSession, Depends(get_session)]):
    """Mock dependency function that depends on another dependency."""
    return SimpleValidator(session)


app = FastAPI()


@app.get("/test")
def test_endpoint(
    validator: Annotated[SimpleValidator, Depends(get_validator)],
    province: str | None = Query(None, max_length=100),
    region: str | None = Query(None, max_length=100),
):
    return {"status": "ok"}


if __name__ == "__main__":
    print("SUCCESS: Nested dependency test worked")
