from abc import ABC, abstractmethod

# This class will be significantly more complicated than data_sensor

class MotionSensor(ABC):

    @ abstractmethod
    def get_data(self):
        pass
