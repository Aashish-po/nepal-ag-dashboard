#!/usr/bin/env python3
"""Test script to isolate the import issue."""

try:
    print("Attempting to import districts router...")
    from api.db import get_db

    print(f"get_db function found: {get_db}")
    print("SUCCESS: Imported districts router")
except ImportError as e:
    print(f"ERROR: Failed to import districts router: {e}")
    import traceback

    traceback.print_exc()
