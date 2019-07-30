
FROM jhphan/geneflow:1.7.0--sing3.3.0-rc.2

WORKDIR /workflow
COPY . /workflow

RUN mkdir /data && geneflow install-workflow --make_apps .

