from concurrent import futures
import logging
import argparse
from time import time

import cv2

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


def video_processing(blob_name, file_path):
    output_file_path = '/tmp/output-' + blob_name
    video = cv2.VideoCapture(file_path)
    
    width = int(video.get(3))
    height = int(video.get(4))
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_file_path, fourcc, 20.0, (width, height))
    
    start = time()
    while(video.isOpened()):
        # print("Read a frame")
        ret, frame = video.read()

        if ret:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            im = cv2.imwrite('/tmp/frame.jpg', gray_frame)
            gray_frame = cv2.imread('/tmp/frame.jpg')
            out.write(gray_frame)
        else:
            break
            
    latency = time() - start
    
    video.release()
    out.release()
    return latency, output_file_path

class Greeter(fibonacci_pb2_grpc.GreeterServicer):

    def __init__(self):
        self.cnt = 0
        self.vids = ["SampleVideo_1280x720_30mb.mp4", "SampleVideo_640x360_30mb.mp4", 
                    "SampleVideo_1280x720_10mb.mp4", "SampleVideo_640x360_10mb.mp4", 
                    "SampleVideo_1280x720_2mb.mp4", "SampleVideo_640x360_2mb.mp4"]
        

    def SayHello(self, request, context):
        if request.name == "record":
            video_filename = "SampleVideo_1280x720_2mb.mp4"
        elif request.name == "replay":
            video_filename = "SampleVideo_640x360_2mb.mp4"
        elif request.name == "hd2":
            video_filename = "SampleVideo_1280x720_2mb.mp4"
        elif request.name == "hd10":
            video_filename = "SampleVideo_1280x720_10mb.mp4"
        elif request.name == "hd30":
            video_filename = "SampleVideo_1280x720_30mb.mp4"
        elif request.name == "lowres2":
            video_filename = "SampleVideo_640x360_2mb.mp4"
        elif request.name == "lowreshd10":
            video_filename = "SampleVideo_640x360_10mb.mp4"
        elif request.name == "lowres30":
            video_filename = "SampleVideo_640x360_30mb.mp4"
        else:
            video_filename = self.vids[self.cnt%len(self.vids)]
            self.cnt += 1


        lat, _ = video_processing(f"output-{request.name}-0", video_filename)
        msg = "fn: VideoProcess | video: %s, lat: %f | runtime: python" % (f"{video_filename}", lat)
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
