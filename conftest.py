"""
Root conftest.py — sets test-safe environment variables BEFORE any app module
is imported, so the app boots with an in-memory SQLite database and a fixed
JWT secret. This makes every test hermetic: no pre-existing .env, no seeded
production database, and no leftover state between runs.
"""
import os
import pytest

# ── Must be set before importing backend.app.core.config ──────────────────────
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-for-ci-only")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_claim_agent.db")
os.environ.setdefault("LLM_PROVIDER", "local")
os.environ.setdefault("APP_ENV", "test")


@pytest.fixture(autouse=True, scope="session")
def seed_test_db():
    """
    Seed the test database once per session so API tests that query claims,
    users, and policies find the expected demo data.
    """
    from backend.app.core.database import engine, Base
    from backend.seed_data import seed_database

    Base.metadata.create_all(bind=engine)
    seed_database()
    yield
    # Teardown: drop all tables so next session starts clean
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True, scope="session")
def cleanup_test_db():
    """Remove the test database file after the session completes."""
    yield
    import pathlib
    db_path = pathlib.Path("test_claim_agent.db")
    if db_path.exists():
        db_path.unlink()
