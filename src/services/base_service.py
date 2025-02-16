from abc import ABC, abstractmethod

from src.dto.basedto import DTO
from src.model.dao import DAO
from src.utils.singleton import Singleton

class Service(ABC, Singleton):
    pass

class DAOService(Service):

    @property
    @abstractmethod
    def _DAO(self) -> DAO:
        pass

    @abstractmethod
    def get_one(self, *args, **kwargs) -> DTO:
        pass

    @abstractmethod
    def get_all(self) -> DTO:
        pass

    @abstractmethod
    def add(self, *args, **kwargs) -> DTO:
        pass
