
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


# build final container

FROM python:3.6.7-alpine3.8

COPY --from=singularity_builder /opt/singularity /opt/singularity

WORKDIR /src
COPY . /src/geneflow

RUN apk update \
    && apk add --no-cache --virtual .build-deps build-base libffi-dev openssl-dev \
    && apk add --no-cache git squashfs-tools libseccomp sudo coreutils \
    && pip install -U pip \
    && git clone -b v0.7.3 https://github.com/TACC/agavepy \
    && pip install ./agavepy \
    && pip install ./geneflow \
    && rm -rf /src/* \
    && rm -rf /root/.cache/pip/* \
    && apk del .build-deps
    
ENV PATH /opt/singularity/bin:$PATH
