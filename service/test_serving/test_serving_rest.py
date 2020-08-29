import requests
import imageio

from config import Config

SERVER_URL = f'http://{Config.TF_SERVE_SERVER}:8501/v1/models/ssd_mobilenet_v1_coco:predict'
IMAGE_URL = 'https://tensorflow.org/images/blogs/serving/cat.jpg'

def main():
    # Compose a JSON Predict request (send JPEG image).
    jpeg_bytes = imageio.imread(IMAGE_URL)
    predict_request = {"instances": [jpeg_bytes.tolist()]}

    # Send few requests to warm-up the model.
    for _ in range(3):
        response = requests.post(SERVER_URL, json=predict_request)
        response.raise_for_status()

    # Send few actual requests and report average latency.
    total_time = 0
    num_requests = 5
    for _ in range(num_requests):
        response = requests.post(SERVER_URL, json=predict_request)
        response.raise_for_status()
        total_time += response.elapsed.total_seconds()

    print('Avg latency: {} ms'.format((total_time*1000)/num_requests))


if __name__ == '__main__':
    main()
