from .._base_module.inferencer import BaseInferencer

import os
import time
import cv2
import numpy as np

from config import Config

USE_GRPC = Config.USE_GRPC
if USE_GRPC:
    import sys
    sys.path.append("service/protos")

    from tensorflow_serving.apis import predict_pb2
    from tensorflow_serving.apis import prediction_service_pb2
    from tensorflow.core.framework import tensor_pb2
    from tensorflow.core.framework import tensor_shape_pb2
    from tensorflow.core.framework import types_pb2

    import grpc
else:
    import requests


class InferencerTFServing(BaseInferencer):
    """Process Data received from Camera Stream using a model deployed with Tensorflow serving"""
    GRPC_HOST = f"{Config.TF_SERVE_SERVER}:8500"
    REST_URL = f'http://{Config.TF_SERVE_SERVER}:8501/v1/models/ssd_mobilenet_v1_coco:predict'
    TARGET_CLASS_ID = 1
    THRESHOLD = 0.35

    def __init__(self, worker):
        self.__worker = worker
        if USE_GRPC:
            channel = grpc.insecure_channel(self.GRPC_HOST)
            self.stub = prediction_service_pb2.PredictionServiceStub(channel)

    def _fetch_rest(self, frame):
        """Send a POST request to Tensorflow serving to detect objects in frame

        Args:
            frame (np.array: a raw image received from a Camera

        Returns:
            detection_boxes (np.array: an array of bounding boxes for detected objects in the frame,
            detection_scores (np.array: an array of confidence scores for detected classes,
            detection_classes (np.array: an array of corresponding classes for each detected box.
        """
        predict_request = {"instances": [frame.tolist()]}
        response = requests.post(self.REST_URL, json=predict_request)
        response.raise_for_status()

        self.logger.debug(
            f"{self.__worker.id}: took {response.elapsed.total_seconds()} seconds to process!")

        predictions = response.json()['predictions'][0]

        detection_boxes = np.array(predictions["detection_boxes"])
        detection_scores = np.array(predictions["detection_scores"])
        detection_classes = np.array(predictions["detection_classes"])

        return detection_boxes, detection_scores, detection_classes

    def _fetch_grpc(self, frame):
        """send a message using gRPC interface to Tensorflow Serving to detect objects in frame

        Args:
            frame (np.array: a raw image received from a Camera

        Returns:
            detection_boxes (np.array: an array of bounding boxes for detected objects in the frame,
            detection_scores (np.array: an array of confidence scores for detected classes,
            detection_classes (np.array: an array of corresponding classes for each detected box.
        """
        tt = time.time()
        # create request
        request = predict_pb2.PredictRequest()
        request.model_spec.name = 'ssd_mobilenet_v1_coco'
        request.model_spec.signature_name = 'serving_default'

        # convert to tensor proto and make request
        # ensure NHWC shape and build tensor proto
        tensor_shape = [1]+list(frame.shape)
        dims = [tensor_shape_pb2.TensorShapeProto.Dim(
            size=dim) for dim in tensor_shape]
        tensor_shape = tensor_shape_pb2.TensorShapeProto(dim=dims)
        tensor = tensor_pb2.TensorProto(
            dtype=types_pb2.DT_UINT8,
            tensor_shape=tensor_shape,
            int_val=list(frame.reshape(-1)))
        request.inputs['inputs'].CopyFrom(tensor)
        resp = self.stub.Predict(request, 30.0)

        self.logger.debug(
            f"{self.__worker.id}: took {time.time() - tt} seconds to process!")

        detection_scores = np.array(resp.outputs["detection_scores"].float_val)
        detection_classes = np.array(
            resp.outputs["detection_classes"].float_val)
        detection_boxes = np.array(
            resp.outputs["detection_boxes"].float_val).reshape(-1, 4)

        return detection_boxes, detection_scores, detection_classes

    def process(self, frame):
        """Process raw images received from a Camera

        Returns:
            list[tuple((int, int), (int, int))]: A list of boxes 
                formed using two points in 2D space (p1, p2).
        """
        if frame is None:
            return None

        width = int(self.__worker.config.width)
        height = int(self.__worker.config.height)

        _fetcher = self._fetch_grpc if USE_GRPC else self._fetch_rest
        detection_boxes, detection_scores, detection_classes = _fetcher(frame)

        filter_1 = detection_scores > self.THRESHOLD
        filter_2 = detection_classes == self.TARGET_CLASS_ID

        raw_boxes = detection_boxes[filter_1 * filter_2]

        boxes = []
        for _box in raw_boxes:
            pt1_h, pt1_w, pt2_h, pt2_w = _box
            pt1_h, pt1_w = int(pt1_h * height), int(pt1_w * width)
            pt2_h, pt2_w = int(pt2_h * height), int(pt2_w * width)
            boxes.append([(pt1_w, pt1_h), (pt2_w, pt2_h)])

        self.logger.debug(f"{self.__worker.id}:Boxes: {boxes}")
        return boxes


"""
import tensorflow.compat.v1 as tf

class BaseModel:
    def __init__(self, worker):
        self.__worker = worker

        model_path = "tf_serving/object_detection/models/ssd_mobilenet_v1_coco"
        detection_graph = self.load_model(model_path)
        self.sess = tf.InteractiveSession(graph=detection_graph)
        self.init_tensors(detection_graph)

    @staticmethod
    def load_model(model_path):
        # Path to frozen detection graph.
        # This is the actual model that is used for the object detection.
        path_to_ckpt = os.path.join(model_path, "frozen_inference_graph.pb")

        # Load a (frozen) Tensorflow model into memory.
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.io.gfile.GFile(path_to_ckpt, "rb") as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name="")

        return detection_graph

    def init_tensors(self, detection_graph):
        raise Exception("Needs to Be implemented!")


class InferencerLocal(BaseModel, BaseInferencer):

    def init_tensors(self, detection_graph):
        self.image_tensor = detection_graph.get_tensor_by_name("image_tensor:0")
        self.detection_boxes = detection_graph.get_tensor_by_name("detection_boxes:0")
        self.detection_scores = detection_graph.get_tensor_by_name("detection_scores:0")
        self.detection_classes = detection_graph.get_tensor_by_name(
            "detection_classes:0"
        )
        self.num_detections = detection_graph.get_tensor_by_name("num_detections:0")

    def process(self, frame):
        # Actual detection.
        input_frame = frame

        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(input_frame, axis=0)
        (boxes, scores, classes, num) = self.sess.run(
            [
                self.detection_boxes,
                self.detection_scores,
                self.detection_classes,
                self.num_detections,
            ],
            feed_dict={self.image_tensor: image_np_expanded},
        )

        classes = np.squeeze(classes).astype(np.int32)
        boxes = np.squeeze(boxes)
        scores = np.squeeze(scores)
        pedestrian_score_threshold = 0.35
        pedestrian_boxes = []
        total_pedestrians = 0
        target_class_id = 1

        height, width = frame.shape[:2]
        for i in range(int(num[0])):
            class_id = classes[i]
            if class_id == target_class_id and scores[i] > pedestrian_score_threshold:
                total_pedestrians += 1
                # score_pedestrian = scores[i]

                pt1_h, pt1_w, pt2_h, pt2_w = boxes[i]
                pt1_h, pt1_w, pt2_h, pt2_w = int(pt1_h * height), int(pt1_w * width), int(pt2_h * height), int(
                    pt2_w * width)

                pedestrian_boxes.append([(pt1_w, pt1_h), (pt2_w, pt2_h)])

        return pedestrian_boxes
"""

Inferencer = InferencerTFServing  # InferencerLocal

if __name__ == "__main__":
    class Worker:
        class Config:
            width = 1280
            height = 720

        id = 1
        config = Config()

    dModel = InferencerTFServing(Worker())

    for image in os.listdir("service/data/images"):
        test_img_path = f"service/data/images/{image}"

        test_img = cv2.imread(test_img_path)
        detected_boxes = dModel.process(test_img)
        for box in detected_boxes:
            p1, p2 = box
            cv2.rectangle(test_img, p1, p2, (255, 0, 0), 2)

        cv2.imshow('Main', test_img)
        cv2.waitKey()
