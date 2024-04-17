from concurrent import futures
import logging
import argparse
from time import time
import grpc

import numpy as np
from time import time

from grpc_reflection.v1alpha import reflection

from proto.fibonacci import fibonacci_pb2
import fibonacci_pb2_grpc
import re
import os
import sys

import pickle
import torch
import rnn

print("python version: %s" % sys.version)
print("Server has PID: %d" % os.getpid())
GRPC_PORT_ADDRESS = os.getenv("GRPC_PORT")

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--addr", dest="addr", default="0.0.0.0", help="IP address")
parser.add_argument("-p", "--port", dest="port", default="50051", help="serve port")
parser.add_argument("-zipkin", "--zipkin", dest="url", default="http://0.0.0.0:9411/api/v2/spans", help="Zipkin endpoint url")
args = parser.parse_args()


class Greeter(fibonacci_pb2_grpc.GreeterServicer):

    def __init__(self):
        model_path = "rnn_model.pth"
        params_path = "rnn_params.pkl"
        with open(params_path, 'rb') as pkl:
            params = pickle.load(pkl)
        all_categories = params['all_categories']
        n_categories = params['n_categories']
        all_letters = params['all_letters']
        n_letters = params['n_letters']
        self.rnn_model = rnn.RNN(n_letters, 128, n_letters, all_categories, n_categories, all_letters, n_letters)
        self.rnn_model.load_state_dict(torch.load(model_path))
        self.rnn_model.eval()

    def predict(self, input_chars):
        start = time()
        output_names = list(self.rnn_model.samples("English", input_chars))
        latency = time() - start
        return latency, output_names

    def SayHello(self, request, context):
        input_chars = request.name
        lat, res = self.predict(input_chars)
        msg = "fn: Model Serving RNN | input: %s, pred: %s, lat: %f | runtime: python" % (request.name, res[0], lat)
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
