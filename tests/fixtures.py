import pytest


@pytest.fixture()
def db_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(
        "postgresql+psycopg2://postgres:docker@localhost:5432/postgres"
    )
    Session = sessionmaker(bind=engine)

    session = Session()

    return session
