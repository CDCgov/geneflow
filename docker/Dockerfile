
# build singularity

FROM golang:1.11.2-alpine3.8 as singularity_builder 

RUN apk update \
    && apk add --no-cache \
   	    ca-certificates \
    	build-base \
	    linux-headers \
    	git \
	    openssl-dev \
    	util-linux-dev \
	    libseccomp-dev \
    	gawk \
    && mkdir -p $GOPATH/src/github.com/sylabs \
    && cd $GOPATH/src/github.com/sylabs \
    && git clone -b v3.0.1 https://github.com/sylabs/singularity.git \
    && cd $GOPATH/src/github.com/sylabs/singularity \
    && ./mconfig -s -S -p /opt/singularity \
    && cd $GOPATH/src/github.com/sylabs/singularity/builddir \
    && make \
    && make install


# build geneflow python wheels

FROM python:3.6.7-alpine3.8 as geneflow_builder

RUN apk update \
    && apk add \
        build-base \
        libffi-dev \
        openssl-dev

WORKDIR /src
COPY . /src
RUN pip install -U pip \
    && pip wheel -w /wheels . 


# build final container

FROM python:3.6.7-alpine3.8

COPY --from=singularity_builder /opt/singularity /opt/singularity
COPY --from=geneflow_builder /wheels /wheels
COPY --from=geneflow_builder /src/docker/requirements-docker.txt /wheels/requirements.txt

RUN apk update \
    && apk add --no-cache git squashfs-tools libseccomp sudo coreutils \
    && pip install -U pip \
    && pip install -f /wheels -r /wheels/requirements.txt \
    && rm -rf /wheels \
    && rm -rf /root/.cache/pip/*
    
ENV PATH /opt/singularity/bin:$PATH
