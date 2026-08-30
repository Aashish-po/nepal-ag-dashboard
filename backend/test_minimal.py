"""Minimal test to reproduce the FastAPI dependency issue."""

from typing import Annotated

from fastapi import Depends, FastAPI, Query
from sqlalchemy.orm import Session


# Mock classes for testing
class MockSession:
    pass


class MockValidator:
    def validate_province(self, province):
        return True

    def validate_region(self, region):
        return True


def get_db():
    """Mock dependency function."""
    yield MockSession()


def get_filter_validator(db: Session):
    """Mock dependency function."""
    return MockValidator()


app = FastAPI()


@app.get("/test")
def test_endpoint(
    db: Annotated[Session, Depends(get_db)],
    province: str | None = Query(None, max_length=100),
    region: str | None = Query(None, max_length=100),
):
    return {"status": "ok"}


if __name__ == "__main__":
    print("SUCCESS: Minimal test with only db worked")
