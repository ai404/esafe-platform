from .modules import camera_module
import logging
import os

logger = logging.getLogger(__name__)


class Service:
    """Register given device modules and run all inference pipelines"""

    def __init__(self):
        self._modules = []

    def register_module(self, module):
        self._modules.append(module)

    def _gen_device_handlers(self):
        for module in self._modules:
            yield module.Handler(module)

    def run(self):
        for device_handler in self._gen_device_handlers():
            device_handler.start()
        logger.info("All handlers are running!")

    def notify(self, device_id, kind, message):
        pass


def main():
    levels = {
        "debug": 10,
        "info": 20,
        "warning": 30
    }
    logging_level = levels.get(os.environ.get("LOGGING_LEVEL", "debug"), 10)
    logging.basicConfig(format='%(levelname)s:%(asctime)s [%(pathname)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging_level)

    service = Service()
    service.register_module(camera_module)

    service.run()


if __name__ == "__main__":
    main()
