#!/bin/bash

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
cd ${SCRIPT_DIR}/..
docker build -f ./docker/Dockerfile -t geneflow:$(cat ${SCRIPT_DIR}/../VERSION)-sing-3.1.1 .

