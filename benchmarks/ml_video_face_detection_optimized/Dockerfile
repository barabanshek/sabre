#---------- PYTHON -----------#
## First stage (Builder):
## Install gRPC and all other dependencies
FROM vhiveease/python-slim:latest as modelServingVideoFaceDetectionPythonBuilder
WORKDIR /py
COPY requirements.txt ./
RUN pip3 install --user -r requirements.txt
COPY server.py ./
ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/v0.3.0/proto/fibonacci/fibonacci_pb2_grpc.py ./
ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/v0.3.0/proto/fibonacci/fibonacci_pb2.py ./proto/fibonacci/

# Download data 
COPY data ./

# Second stage (Runner):
FROM vhiveease/python-slim:latest as modelServingVideoFaceDetectionPython
RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0
COPY --from=modelServingVideoFaceDetectionPythonBuilder /root/.local /root/.local
COPY --from=modelServingVideoFaceDetectionPythonBuilder /py /app
WORKDIR /app
# ENV PATH=/root/.local/bin:$PATH
ENTRYPOINT [ "python", "/app/server.py" ]
