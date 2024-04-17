from concurrent import futures
import logging
import argparse
from time import time
import grpc

import pandas as pd
# import numpy as np
import joblib 

from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.linear_model import LogisticRegression
# from sklearn.externals import joblib


from grpc_reflection.v1alpha import reflection

from proto.fibonacci import fibonacci_pb2
import fibonacci_pb2_grpc
import re
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



cleanup_re = re.compile('[^a-z]+')
def cleanup(sentence):
    sentence = sentence.lower()
    sentence = cleanup_re.sub(' ', sentence).strip()
    return sentence

def predict(model_path, tfidf_data_path,  input_data):
    df = pd.read_csv(tfidf_data_path)

    start = time()
    df['train'] = df['Text'].apply(cleanup)

    tfidf_vect = TfidfVectorizer(min_df=100).fit(df['train'])

    df_input = pd.DataFrame()
    df_input['x']  = [input_data]
    df_input['x'] = df_input['x'].apply(cleanup)
    X = tfidf_vect.transform(df_input['x'])

    model = joblib.load(model_path)
    y = model.predict(X)
    latency = time() - start

    return y, latency


class Greeter(fibonacci_pb2_grpc.GreeterServicer):

    def __init__(self):
        self.training_filenames = ["reviews10mb.csv", "reviews20mb.csv", "reviews50mb.csv", "reviews100mb.csv"]
    

    def SayHello(self, request, context):
        training_file = "reviews10mb.csv"
        model_path = "lr-model"

        pred, lat = predict(model_path, training_file, request.name)
        msg = "fn: Model Serving LR | input: %s, pred: %i, lat: %f | runtime: python" % (request.name, pred, lat)
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
