ARG runtime=python3.11

FROM python:3.11 AS build

WORKDIR /operator-build

ADD aws-opentelemetry-distro ./aws-opentelemetry-distro/

# Remove opentelemetry-exporter-otlp-proto-grpc and grpcio, as grpcio has strict dependencies on the Python version and
# will cause confusing failures if gRPC protocol is used. Now if gRPC protocol is requested by the user, instrumentation
# will complain that grpc is not installed, which is more understandable. References:
# * https://github.com/open-telemetry/opentelemetry-operator/blob/b5bb0ae34720d4be2d229dafecb87b61b37699b0/autoinstrumentation/python/requirements.txt#L2
# * https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/azure-functions/recover-python-functions.md#troubleshoot-cannot-import-cygrpc
RUN sed -i "/opentelemetry-exporter-otlp-proto-grpc/d" ./aws-opentelemetry-distro/pyproject.toml

RUN mkdir workspace && pip install --target workspace ./aws-opentelemetry-distro

FROM public.ecr.aws/sam/build-${runtime}

ADD . /workspace

WORKDIR /workspace

RUN mkdir -p /build

COPY --from=build /operator-build/workspace /build/python

RUN mv otel_sdk/otel_wrapper.py /build/python && \
    mv otel_sdk/otel-instrument /build && \
    chmod 755 /build/otel-instrument && \
    rm -rf /build/python/boto* && \
    rm -rf /build/python/urllib3* && \
    cd /build && \
    zip -r opentelemetry-python-layer.zip otel-instrument python

#  sed -i "/opentelemetry-exporter-otlp-proto-grpc/d" ./aws-opentelemetry-distro/pyproject.toml \
#  python3 -m pip install ./aws-opentelemetry-distro -t /build/python && \
  # python3 -m pip install -r otel_sdk/nodeps-requirements.txt -t /build/tmp --no-deps && \
  # We need to use a `/build/tmp/` folder otherwise the instrumentation packages
  # do not get fully downloaded to the `opentelemetry/instrumentation/` path.
  # cp -r /build/tmp/* /build/python/ && \
  # rm -rf /build/tmp && \
#  mv otel_sdk/otel_wrapper.py /build/python && \
#  mv otel_sdk/otel-instrument /build && \
#  chmod 755 /build/otel-instrument && \
#  rm -rf /build/python/boto* && \
#  rm -rf /build/python/urllib3* && \
#  cd /build && \
#  zip -r opentelemetry-python-layer.zip otel-instrument python

CMD cp /build/opentelemetry-python-layer.zip /out/opentelemetry-python-layer.zip
