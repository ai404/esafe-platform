from service.mixins import LoggerMixin

from threading import Thread
import time

from database.models.main.device._device import Device

from typing import Type


class BaseHandler(LoggerMixin, Thread):
    """Run workers for different device types

    This class is used to continously listen for device's configurations change,
    run / stop and refresh updated configurations within workers.

    Args:
        module (Python module): A python module encapsulating 
            the implementation of a Worker, Reader, Handler and an Inferencer
            to use with a given device pool.
        sleep_time (int, optional): Time in seconds to pause 
            between each loops. Defaults to 5 seconds.
    """

    def __init__(self, module, sleep_time: int = 5):
        super(BaseHandler, self).__init__()

        self._running_workers = {}
        self._module = module
        self._sleep_time = sleep_time

    def _worker_is_running(self, config: Type[Device]):
        """Check if a device has worker running"""
        try:
            return self._running_workers[config.id].isAlive()
        except:
            return False

    def run_update_worker(self, config: Type[Device]):
        """run / stop or refresh a worker's configuration"""
        if self._worker_is_running(config):
            if not config.active:
                self.stop_worker(config)
            else:
                self.logger.debug(f"{config.get_name()}: updating worker")
                self._running_workers[config.id].config = config
        elif config.active:
            self.start_worker(config)
        else:
            self.stop_worker(config)

    def start_worker(self, config: Type[Device]):
        """Start a worker and a reader threads with the given configuration."""
        if config.active:
            self.logger.info(f"{config.get_name()}: starting worker")
            worker = self._module.Worker(self, config)
            reader = self._module.Reader(config)
            reader.start()
            worker.set_reader(reader)
            worker.set_inferencer(self._module.Inferencer(worker))
            worker.start()

            self._running_workers[config.id] = worker

    def stop_worker(self, config: Type[Device]):
        """Stop the worker with the given configuration."""
        if self._worker_is_running(config):
            self.logger.info(f"{config.get_name()}: stopping worker")
            self._running_workers[config.id].stop()
            del self._running_workers[config.id]

    def get_devices_config(self):
        """Get selected devices"""
        raise NotImplementedError

    def run(self):
        """Continously listen to devices configuration and update for running workers."""
        while True:
            for config in self.get_devices_config():
                self.run_update_worker(config)
            time.sleep(self._sleep_time)
