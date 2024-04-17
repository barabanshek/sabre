from concurrent import futures
import logging
import argparse
from time import time

from PIL import Image

import grpc
import string

from grpc_reflection.v1alpha import reflection

from proto.fibonacci import fibonacci_pb2
import fibonacci_pb2_grpc

import os
import sys

print("python version: %s" % sys.version)
print("Server has PID: %d" % os.getpid())
GRPC_PORT_ADDRESS = os.getenv("GRPC_PORT")

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--addr", dest="addr", default="0.0.0.0", help="IP address")
parser.add_argument("-p", "--port", dest="port", default="50051", help="serve port")
parser.add_argument("-zipkin", "--zipkin", dest="url", default="http://0.0.0.0:9411/api/v2/spans", help="Zipkin endpoint url")
args = parser.parse_args()


import ops

def image_processing(file_name, image_path):
    path_list = []
    start = time()
    with Image.open(image_path) as image:
        tmp = image
        path_list += ops.flip(image, file_name)
        path_list += ops.rotate(image, file_name)
        path_list += ops.filter(image, file_name)
        path_list += ops.gray_scale(image, file_name)
        path_list += ops.resize(image, file_name)

    latency = time() - start
    return latency, path_list


class Greeter(fibonacci_pb2_grpc.GreeterServicer):

    def __init__(self):
        extension = "jpg"
        hd_resolution = "3840x"
        low_resolution = "1136x"
        self.hd_images = [file for file in os.listdir(".") if file.endswith(f".{extension}") and (f"{hd_resolution}" in file)]
        self.hd_image_cnt = 0
        self.low_images = [file for file in os.listdir(".") if file.endswith(f".{extension}") and (f"{low_resolution}" in file)]
        self.low_image_cnt = 0

    def SayHello(self, request, context):

        img_filename = ""
        if request.name == "record":
            img_filename = "image.jpg"
        elif request.name == "replay":
            img_filename= "animal-dog.jpg"
        elif request.name == "hd":
            img_filename = self.hd_images[self.hd_image_cnt]
            self.hd_image_cnt = (self.hd_image_cnt + 1) % len(self.hd_images)
        else:
            img_filename = self.low_images[self.low_image_cnt]
            self.low_image_cnt = (self.low_image_cnt + 1) % len(self.low_images)

        lat, _ = image_processing(f'{img_filename}', img_filename)

        msg = "fn: ImageProcess | img: %s, lat: %f | runtime: python" % (img_filename, lat)
        return fibonacci_pb2.HelloReply(message=msg)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    fibonacci_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)

    print("Enabling Reflection")
    SERVICE_NAMES = (
        fibonacci_pb2.DESCRIPTOR.services_by_name['Greeter'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    address = ('[::]:' + GRPC_PORT_ADDRESS if GRPC_PORT_ADDRESS else  '[::]:50051')
    server.add_insecure_port(address) 

    logging.info("Start server: listen on : " + address)

    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()
