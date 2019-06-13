from abc import ABC, abstractmethod

class DataSensor(ABC):

    @ abstractmethod
    def get_data(self):
        pass
