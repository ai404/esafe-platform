import grpc
import cv2
import time
import numpy as np
import imageio

import sys
sys.path.append("service/protos")
sys.path.append("./")

from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2
from tensorflow.core.framework import tensor_pb2
from tensorflow.core.framework import tensor_shape_pb2
from tensorflow.core.framework import types_pb2

from config import Config

HOST = f'{Config.TF_SERVE_SERVER}:8500'
IMAGE_URL = 'https://tensorflow.org/images/blogs/serving/cat.jpg'


def main():
    # create prediction service client stub
    channel = grpc.insecure_channel(HOST)
    stub = prediction_service_pb2.PredictionServiceStub(channel)

    # read image into numpy array
    img = imageio.imread(IMAGE_URL)

    tt = time.time()
    # create request
    request = predict_pb2.PredictRequest()
    request.model_spec.name = 'ssd_mobilenet_v1_coco'
    request.model_spec.signature_name = 'serving_default'

    # convert to tensor proto and make request
    tensor_shape = [1]+list(img.shape)
    dims = [tensor_shape_pb2.TensorShapeProto.Dim(
        size=dim) for dim in tensor_shape]
    tensor_shape = tensor_shape_pb2.TensorShapeProto(dim=dims)
    tensor = tensor_pb2.TensorProto(
        dtype=types_pb2.DT_UINT8,
        tensor_shape=tensor_shape,
        int_val=list(img.reshape(-1)))
    request.inputs['inputs'].CopyFrom(tensor)
    resp = stub.Predict(request, 30.0)

    print('total time: {}s'.format(time.time() - tt))


if __name__ == '__main__':
    main()
