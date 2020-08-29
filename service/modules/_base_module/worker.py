from service.mixins import LoggerMixin

import time

from threading import Thread

from database.models.main.device._device import Device
from .reader import BaseReader
from .inferencer import BaseInferencer
from .handler import BaseHandler

from typing import Type


class BaseWorker(LoggerMixin, Thread):
    """Worker performing the inference pipeline"""

    def __init__(self, handler: Type[BaseHandler], config: Type[Device]):
        super(BaseWorker, self).__init__()

        self.id = config.get_name()

        self._handler = handler
        self._config = config

        self._is_running = True
        self._reader = None
        self._inferencer = None
        self._notifications = []

    def set_reader(self, reader: Type[BaseReader]):
        """Set data reader for given Device type"""
        self._reader = reader

    def set_inferencer(self, inferencer: Type[BaseInferencer]):
        """Set inferencer for given Device type"""
        self._inferencer = inferencer

    def config_processor(self, config: Type[Device]):
        """Optional processing on device configuration"""
        pass

    @property
    def config(self) -> Type[Device]:
        """Returns Device configuration object"""
        return self._config

    @config.setter
    def config(self, new_config: Type[Device]):
        """Update Device configuration object"""
        self._config = new_config
        self.config_processor(new_config)

    def stop(self):
        """Stop Worker Thread"""
        self._is_running = False

    def _one_loop(self):
        """One loop implementation

        Returns:
            tuple[np.array, np.array]: 
                data: raw data from device, 
                processed_data: processed data after inference.
        """
        self.logger.debug(f"{self.id}: starting loop")
        data = self._reader.get()
        processed_data = self._inferencer.process(data)
        return data, processed_data

    def run(self):
        """Continously loop while the device is active and the thread is running"""
        while self.config.active and self._is_running:
            try:
                self._one_loop()
            except:
                self.logger.exception(f"{self.id}: looping crashed!")
            time.sleep(1e-3)

        self._reader.release()
