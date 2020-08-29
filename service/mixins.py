from database import models, db_session

from scipy.spatial.distance import pdist
from flask_socketio import SocketIO

import cv2
import itertools
import base64
import datetime

import numpy as np

import logging
import os

from config import Config

class HomographyMixin:
    """A mixin to prepare required matrices to get a bird eye perspective of an image"""

    def __init__(self, *args, **kwargs):
        self._metadata = None
        self._homography = None
        super().__init__(*args, **kwargs)

    def _calculate_homography(self):
        """Calculate a homography using the calibration points

        Returns:
            np.array: A 3x3 numpy array
        """
        src = np.array(self._metadata[:4])

        h_units = self._config.h_units
        v_units = self._config.v_units
        dst = np.array(
            [(0, v_units), (h_units, v_units), (0, 0), (h_units, 0)])

        h_m, _ = cv2.findHomography(src, dst)
        self.logger.info(f"{self.id}: homography calculated")
        return h_m

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, new_value):
        if self._metadata != new_value:
            self._metadata = new_value
            self.logger.info(
                f"{self.id}: _metadata value updated to {new_value}")

            if new_value is not None:
                self._homography = self._calculate_homography()

    @staticmethod
    def _parse_metadata(config):
        """Parse device metadata to extract calibration points"""
        if not config.active or config.device_metadata is None:
            return None

        width, height = config.width, config.height
        points = []
        for point in config.device_metadata.split("|"):
            try:
                x, y = point.split(";")
                points.append([float(x) * width, float(y) * height])
            except:
                return None

        if len(points) != 4:
            return None

        return points

    def config_processor(self, new_config):
        self.logger.debug(f"{self.id}: updating config")
        self.metadata = self._parse_metadata(new_config)


class SocialDistancingMixin:
    """A mixin to calculate distances between detected boxes/pedastrians"""

    @staticmethod
    def _calculate_distances(boxes, homography):
        """Calculate a reference marker for each box and calculate 
        bird eye distances between boxes

        Args:
            boxes (list): A list of boxes defined as a tuple of 2D points.
            homography (np.array): A 3x3 numpy array.

        Returns:
            pix_markers (list): A list of marker coordinates defined as tuples,
            distances (np.array): bird eye distances between detected boxes.
        """
        pos_markers = []
        pix_markers = []
        for box in boxes:
            (pt1_w, pt1_h), (pt2_w, pt2_h) = box

            pix_marker = ((pt1_w + pt2_w) // 2, max(pt1_h, pt2_h))
            pix_markers.append(pix_marker)

            pos_marker = np.array(pix_marker).reshape(
                1, 1, 2).astype("float32")
            pos_marker = cv2.perspectiveTransform(
                pos_marker, homography).squeeze()
            pos_markers.append(pos_marker)

        if len(pos_markers) <= 1:
            return np.array([]), np.array([])

        distances = pdist(np.array(pos_markers))
        return pix_markers, distances

    def _gen_segments(self, markers, distances, threshold):
        """Filter segments that are shorter then a given threshold

        Args:
            markers (list): A list of marker coordinates defined as tuples.
            distances (np.array): A list of distances between boxes.
            threshold (float): A threshold used to decide when to generate a distaning alert.

        Returns:
            list: A list of filtered segments with length below the threshold.
        """
        coordinates = list(itertools.combinations(range(len(markers)), 2))
        self.logger.debug(
            f"{self.id}:Distances: {distances} [threshold = {threshold}]")
        indexes, = np.where(distances < threshold)

        segments = []
        for idx in indexes:
            i, j = coordinates[idx]
            segments.append((markers[i], markers[j]))

        self.logger.debug(f"{self.id}:Segments: {segments}")
        return segments

    def _process_boxes(self, boxes):
        """Process boxes to generate segments and filter those that are shorter then a given threshold

        Args:
            boxes (list): A list of boxes defined as a tuple of 2D points.

        Returns:
            list: A list of filtered segments with length below the threshold.
        """
        homography = getattr(self, "_homography", None)
        self.logger.debug(f"Homography: {homography}")
        if homography is None:
            return []

        threshold = self._config.notif_min_units

        pix_markers, distances = self._calculate_distances(boxes, homography)
        return self._gen_segments(pix_markers, distances, threshold)

    @staticmethod
    def _draw_segments(frame, segments):
        """Draw given segments to the given frame"""
        for segment in segments:
            cv2.line(frame, segment[0], segment[1],
                     color=(0, 255, 255), thickness=2)
            cv2.circle(frame, segment[0], radius=3,
                       color=(255, 0, 0), thickness=-1)
            cv2.circle(frame, segment[1], radius=3,
                       color=(255, 0, 0), thickness=-1)

    def _one_loop(self):
        """Extend the parent method to register notifications 
        and process the boxes found by the model to generate segments"""
        frame, processed_data = super()._one_loop()

        if processed_data:
            segments = self._process_boxes(processed_data)
            if len(segments):
                self._draw_segments(frame, segments)
                self._notifications.append({
                    "kind": "distancing"
                })
            if self.config.streaming_output:
                self._notifications.append({
                    "kind": "frame"
                })
        return frame, processed_data


class NotificationMixin:
    """A mixin to persist Generated alerts to database and send 
    real-time notifications to the web application"""

    def __init__(self, *args, **kwargs):
        self.socketio = SocketIO(message_queue=Config.REDIS_SERVER)
        super().__init__(*args, **kwargs)

    def _one_loop(self):
        """Extend the parent method to send notifications/alerts"""
        data, processed_data = super()._one_loop()

        if data is not None:
            while len(self._notifications) > 0:
                notification = self._notifications.pop()
                if notification["kind"] == "frame":
                    self.send_image(self.config.get_name(), data)
                else:
                    self.send_alert(
                        notification["kind"], self.config.entity_name, self.config.location_name)

        return data, processed_data

    def send_image(self, device_id, image):
        """Send an image to the web application on the device's panel

        Args:
            device_id (int): The device id for which the alert is generated.
            image (np.array): The captured image after processing to be sent to the web application.
        """
        self.logger.debug(f"{device_id}: sending processed image!")
        base64_img = base64.b64encode(
            cv2.imencode('.jpg', image)[1].tostring())
        self.socketio.emit(
            "image", {"message": base64_img}, room=f"device-{device_id}")

    def persist_alert(self, alert_type):
        """Save generated alert to database

        Args:
            alert_type (str): Alert string tag.

        Returns:
            int: the id of the alert after saving it to database.
        """
        session = db_session()

        alert = models.Alert()
        alert.alert_type = alert_type
        alert.entity_id = self.config.entity_id

        # TODO change camera_id to device_id
        alert.camera_id = self.config.id
        alert.source_id = self.config.__class__.__name__

        session.add(alert)
        session.commit()

        return alert.id

    def send_alert(self, alert_type, entity_name, location_name):
        """Send alert notification to web application after persisting the alert into database

        Args:
            alert_type (str): Alert string tag.
            entity_name (str): The name of the entity where the alert is generated.
            location_name (str): The name of the facility/location where the alert is generated.
        """
        dtime = datetime.datetime.now().strftime('%d-%b %H:%M')

        alert_id = self.persist_alert(alert_type)
        alert_title = "Social distancing" if alert_type == "distancing" else "Unknown Alert"
        alert_title = "Mask" if alert_type == "mask" else alert_title
        message = f"{alert_title} ({entity_name} / {location_name}): {dtime}"
        self.socketio.emit("alert", {
                           "message": message, "id": alert_id}, room=f"device-{self.config.get_name()}")


class LoggerMixin(object):
    """A mixin to initialize a logger"""
    @property
    def logger(self):
        name = '.'.join([
            self.__module__,
            self.__class__.__name__
        ])
        return logging.getLogger(name)


class MaskDetectionMixin:
    def _one_loop(self):
        data, processed_data = super()._one_loop()
        # TODO: add processing logic here
        return data, processed_data
