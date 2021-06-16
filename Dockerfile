FROM continuumio/miniconda3

ARG APP_DIR=/home/app
RUN mkdir -p ${APP_DIR}

WORKDIR ${APP_DIR}

RUN mkdir scraper/
RUN touch scraper/__init__.py
COPY environment.yml setup.py ./

RUN conda env create -f environment.yml

RUN echo "source activate craiglist_crawler" > ~/.bashrc
ENV PATH /opt/conda/envs/craiglist_crawler/bin:$PATH

ENV SHELL /bin/bash