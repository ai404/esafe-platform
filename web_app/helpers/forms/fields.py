from wtforms import Field
from wtforms.widgets import HiddenInput

# TODO: include html tags for each custom Field
# https://gist.github.com/felipeblassioli/43a57eaa575679463d01

class BoundingBoxField(Field):
    widget = HiddenInput()

    def _value(self):
        return self.data


class CameraPicker(Field):
    widget = HiddenInput()

    def _value(self):
        return self.data


class CameraConfigField(Field):
    widget = HiddenInput()

    def _value(self):
        return self.data
