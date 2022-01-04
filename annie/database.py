import sqlalchemy


from .dto import metadata
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


class Database:
    def __init__(self, connection_string: str) -> None:
        self._engine = create_engine(connection_string, future=True)
        self._session = Session(self._engine)

    @property
    def session(self) -> Session:
        return self._session

    def create_schema(self, overwrite=False):
        if overwrite:
            self.drop_schema()

        metadata.create_all(self._engine)

    def drop_schema(self):
        metadata.drop_all(self._engine)