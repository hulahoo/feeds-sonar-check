from abc import abstractmethod, ABC
from contextlib import contextmanager

from sqlalchemy import create_engine, MetaData
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, Session

from feeds_importing_worker.config.config import settings


class Database(ABC):
    def __init__(self) -> None:
        self.engine = self._create_engine()
        self._session_factory = self._init_session_factory()

    @abstractmethod
    def _get_db_url(self):
        ...

    @abstractmethod
    def _create_engine(self):
        ...

    @abstractmethod
    def _init_session_factory(self):
        ...

    @contextmanager
    def session(self):
        session: Session = self._session_factory()
        try:
            yield session
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


class SyncPostgresDriver(Database):
    def _get_db_url(self):
        return f"postgresql://{settings.db.user}:{settings.db.password}@" \
            f"{settings.db.host}:{settings.db.port}/{settings.db.name}"

    def _create_engine(self) -> Engine:
        return create_engine(
            self._get_db_url(),
            pool_pre_ping=True,
            pool_recycle=3600,
            max_overflow=10,
            pool_size=15,
        )

    def _init_session_factory(self):
        return scoped_session(sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        ))

metadata = MetaData(bind=SyncPostgresDriver().engine)
Base = declarative_base(metadata=metadata)