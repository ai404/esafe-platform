from .._base_module.reader import BaseReader

import cv2
import time


class Reader(BaseReader):
    def _init_interface(self):
        uri = self._config.streaming_uri
        self.logger.info(f"{self._config.get_name()}: reading from URI= {uri}")
        self._interface = cv2.VideoCapture(uri)

        self._width = int(self._config.width)
        self._height = int(self._config.height)

    def _reset_interface(self):
        self.release()
        time.sleep(.1)
        self._init_interface()

    def _preprocess(self, frame):
        return cv2.resize(frame, (self._width, self._height))

    def _read(self):
        success, frame = self._interface.read()
        if not success:
            self._reset_interface()
            return None
        time.sleep(.05)
        return self._preprocess(frame)

    def release(self):
        if self._interface:
            self._interface.release()
