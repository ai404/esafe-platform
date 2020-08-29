from service.mixins import LoggerMixin

from threading import Thread
import time
from database.models.main.device._device import Device

from typing import Type

class BaseReader(LoggerMixin, Thread):
    """Reader class to extract data from devices"""

    def __init__(self, config: Type[Device]):
        super(BaseReader, self).__init__()
        self._config = config
        self._init_interface()
        self._is_running = True
        self._current_data = None

    def _init_interface(self):
        """Initialize an interface to connect to a device"""
        raise NotImplementedError

    def _read(self):
        """Read data from device"""
        raise NotImplementedError

    def release(self):
        """Release interface"""
        raise NotImplementedError

    def get(self):
        """Get the newest data object in memory"""
        return self._current_data

    def run(self):
        """Continously read data from device"""
        while self._is_running:
            self._current_data = self._read()
            time.sleep(.1)
