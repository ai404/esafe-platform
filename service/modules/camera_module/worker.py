from .._base_module.worker import BaseWorker
from service.mixins import NotificationMixin, SocialDistancingMixin, HomographyMixin


class Worker(NotificationMixin, SocialDistancingMixin, HomographyMixin, BaseWorker):
    __name__ = "CameraWorker"
