#!/bin/bash

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
cd ${SCRIPT_DIR}/..
docker build --network=host -f ./docker/Dockerfile -t geneflow:$(cat ${SCRIPT_DIR}/../VERSION)--sing3.2.0 .

