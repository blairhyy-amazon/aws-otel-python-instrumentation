#!/bin/bash
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

# Fail fast
set -e

# Check script is running in contract-tests
current_path=`pwd`
current_dir="${current_path##*/}"
if [ "$current_dir" != "aws-otel-python-instrumentation" ]; then
  echo "Please run from aws-otel-python-instrumentation dir"
  exit
fi


mkdir -p build
docker build --progress plain -t aws-otel-lambda-python-layer -f Dockerfile-lambda .
docker run --rm -v "$(pwd)/build:/out" aws-otel-lambda-python-layer
