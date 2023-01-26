# Define function directory
ARG FUNCTION_DIR="/function"
ARG BASE_IMAGE="python:3.10-slim"

ARG MODEL_PATH
ARG PYTHON_DEPENDENCIES
ARG SYSTEM_DEPENDENCIES

ARG INPUT_COLUMNS


FROM ${BASE_IMAGE} AS build-image

# Install dependencies for aws runtime API
RUN apt-get update && apt-get install -y \
    g++ \
    make \
    cmake \
    unzip \
    libcurl4-openssl-dev

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Create function directory
RUN mkdir -p ${FUNCTION_DIR}

# Copy function code
ARG MODEL_PATH
COPY lambda.py ${FUNCTION_DIR}/
COPY ${MODEL_PATH} ${FUNCTION_DIR}/model.pkl

# Install python dependencies
ARG PYTHON_DEPENDENCIES
RUN  pip install \
     --target ${FUNCTION_DIR} \
        awslambdaric pandas \
        ${PYTHON_DEPENDENCIES}


# Multi-stage build: grab a fresh copy of the base image
ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ARG SYSTEM_DEPENDENCIES
# Install runtime system dependencies
RUN if [ -z "$SYSTEM_DEPENDENCIES" ]; then \
      echo "NO SYSTEM_DEPENDENCIES SPECIFIED"; \
    else \
      apt-get update && apt-get install -y ${SYSTEM_DEPENDENCIES} ; \
    fi

# Include global arg in this stage of the build
ARG FUNCTION_DIR
ENV FUNCTION_DIR=${FUNCTION_DIR}

# Store input columns as env var
ARG INPUT_COLUMNS
ENV INPUT_COLUMNS=${INPUT_COLUMNS}

# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Copy in the build image dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]

CMD [ "lambda.lambda_handler" ]