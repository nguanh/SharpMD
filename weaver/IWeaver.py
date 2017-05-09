
from abc import ABC, abstractmethod


class IWeaver(ABC):
    def __init__(self, limit ):
        self.limit = limit


    @abstractmethod
    def run(self):
        pass

