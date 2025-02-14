from abc import ABC, abstractmethod

class DTO(ABC):
    @abstractmethod
    def tojson(self):
        pass
