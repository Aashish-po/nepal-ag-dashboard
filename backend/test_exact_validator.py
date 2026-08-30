"""Minimal test to reproduce the FastAPI dependency issue with exact validator signature."""

from typing import Annotated

from fastapi import Depends, FastAPI, Query
from sqlalchemy.orm import Session


# Mock classes for testing
class MockSession:
    def execute(self, stmt):
        # Mock execute method
        class MockResult:
            def scalars(self):
                class MockScalars:
                    def all(self):
                        return ["Bagmati", "Madhesh"]  # Mock provinces

                return MockScalars()

        return MockResult()


class SimpleValidator:
    def __init__(self, session: object):
        self.session = session

    def validate_province(self, province):
        return True

    def validate_region(self, region):
        return True


def get_db():
    """Mock dependency function that yields a Session."""
    yield MockSession()


def get_filter_validator(db: Session) -> SimpleValidator:
    """Mock dependency function matching the real signature."""
    return SimpleValidator(db)


app = FastAPI()


@app.get("/test")
def test_endpoint(
    validator: Annotated[SimpleValidator, Depends(get_filter_validator)],
    province: str | None = Query(None, max_length=100),
    region: str | None = Query(None, max_length=100),
):
    return {"status": "ok"}


if __name__ == "__main__":
    print("SUCCESS: Exact validator signature test worked")
