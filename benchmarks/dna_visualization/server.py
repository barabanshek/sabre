from concurrent import futures
import logging
import argparse
from time import time
import grpc
from squiggle import transform

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



class Greeter(fibonacci_pb2_grpc.GreeterServicer):

    def __init__(self):
        self.fasta_files = ["bacillus_subtilis.fasta", "genomic-seq.fasta", "spaced_fasta.fasta", "f002.fasta"] 
        self.cnt = 0

    def visualize(self, fasta_file):
        start = time()
        data = open(fasta_file, "r").read()
        result = transform(data)
        latency = time() - start

        return latency

    def SayHello(self, request, context):
        fasta_file = ""
        if request.name == "record":
            fasta_file = "bacillus_subtilis.fasta"
        elif request.name == "replay":
            fasta_file = "genomic-seq.fasta"
        elif request.name == "small":
            fasta_file = "f002.fasta"
        elif request.name == "medium":
            fasta_file = "spaced_fasta.fasta"
        elif request.name == "big":
            fasta_file = "genomic-seq.fasta"
        elif request.name == "verybig":
            fasta_file = "bacillus_subtilis.fasta"
        else:
            fasta_file = self.fasta_files[self.cnt%len(self.fasta_files)]
            self.cnt += 1

        lat = self.visualize(fasta_file)
        msg = "fn: dna_visualization | fasta_file: %s, lat: %f | runtime: python" % (fasta_file, lat)
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
