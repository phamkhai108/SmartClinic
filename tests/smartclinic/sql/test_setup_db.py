from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from smartclinic.common.base import get_settings
from smartclinic.sql.setup_db import User, setup_db


def test_setup_db_uses_database_url(tmp_path, monkeypatch):
    db_file = tmp_path / "test_setup.db"
    url = f"sqlite:///{db_file}"
    monkeypatch.setenv("SMARTCLINIC_DATABASE_URL", url)
    monkeypatch.setenv("SMARTCLINIC_JWT_SECRET", "test-secret-key-16")
    get_settings.cache_clear()
    setup_db()
    assert db_file.exists()
    engine = create_engine(url)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        assert session.query(User).count() == 2
    get_settings.cache_clear()
