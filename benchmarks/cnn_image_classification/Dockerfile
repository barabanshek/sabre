#---------- PYTHON -----------#
## First stage (Builder):
## Install gRPC and all other dependencies
FROM vhiveease/python-slim:latest as modelServingCNNPythonBuilder
WORKDIR /py
COPY requirements.txt ./
RUN pip3 install --user -r requirements.txt
COPY server.py ./
COPY squeezenet.py ./
ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/v0.3.0/proto/fibonacci/fibonacci_pb2_grpc.py ./
ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/v0.3.0/proto/fibonacci/fibonacci_pb2.py ./proto/fibonacci/

# Download data (training data)
COPY data ./

# Second stage (Runner):
FROM vhiveease/python-slim:latest as modelServingCNNPython
COPY --from=modelServingCNNPythonBuilder /root/.local /root/.local
COPY --from=modelServingCNNPythonBuilder /py /app

COPY imagenet_class_index.json ./root/.keras/models/

WORKDIR /app
# ENV PATH=/root/.local/bin:$PATH
ENTRYPOINT [ "python", "/app/server.py" ]
