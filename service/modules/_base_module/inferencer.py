from service.mixins import LoggerMixin

import numpy as np


class BaseInferencer(LoggerMixin):
    """Used to process data extracted from devices"""

    def process(self, data):
        """Process raw data received from device
        
        Process raw data and apply a model to extract 
        insights from the received data.
        """
        raise NotImplementedError
