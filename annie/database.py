from typing import Iterable
from .dto import metadata
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from .dto import Dto


class Database:
    def __init__(self, connection_string: str='sqlite:///league.db') -> None:
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
    
    def add(self, entity: Iterable[Dto] | Dto):
        self.session.add_all(entity)
        self.session.commit()
            

    def merge(self, entity: Iterable[Dto] | Dto):
        try:
            for n in entity:
                self.session.merge(n)
        except TypeError:
            self.session.merge(entity)