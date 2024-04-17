#---------- PYTHON -----------#
## First stage (Builder):
## Install gRPC and all other dependencies
FROM vhiveease/python-slim:latest as imageProcessingPythonBuilder
WORKDIR /py
COPY requirements.txt ./
RUN pip3 install --user -r requirements.txt
COPY server.py ./
COPY ops.py ./
ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/v0.3.0/proto/fibonacci/fibonacci_pb2_grpc.py ./
ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/v0.3.0/proto/fibonacci/fibonacci_pb2.py ./proto/fibonacci/

# Download data (images)
COPY data ./

# Second stage (Runner):
FROM vhiveease/python-slim:latest as imageProcessingPython
COPY --from=imageProcessingPythonBuilder /root/.local /root/.local
COPY --from=imageProcessingPythonBuilder /py /app
WORKDIR /app
# ENV PATH=/root/.local/bin:$PATH
ENTRYPOINT [ "python", "/app/server.py" ]
