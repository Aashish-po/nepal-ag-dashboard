#!/usr/bin/env python3
"""Minimal test to reproduce the FastAPI dependency issue with real Session."""

from typing import Annotated

from fastapi import Depends, FastAPI, Query
from sqlalchemy.orm import Session


# Mock classes for testing
class SimpleValidator:
    def __init__(self, session: Session):
        self.session = session

    def validate_province(self, province):
        return True

    def validate_region(self, region):
        return True


def get_db():
    """Mock dependency function that yields a Session."""
    yield Session()  # This might not work but let's try


def get_validator(db: Annotated[Session, Depends(get_db)]):
    """Mock dependency function that depends on another dependency."""
    return SimpleValidator(db)


app = FastAPI()


@app.get("/test")
def test_endpoint(
    validator: Annotated[SimpleValidator, Depends(get_validator)],
    province: str | None = Query(None, max_length=100),
    region: str | None = Query(None, max_length=100),
):
    return {"status": "ok"}


if __name__ == "__main__":
    print("SUCCESS: Nested dependency with real Session worked")
