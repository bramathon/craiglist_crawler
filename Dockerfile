FROM continuumio/miniconda3

ADD environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml

RUN echo "source activate craig" > ~/.bashrc
ENV PATH /opt/conda/envs/craig/bin:$PATH

# RUN python -m pip install --upgrade pip \
#  && pip install pipenv==2020.8.13
 
ARG USER=craig
ARG UID=1000
ARG GID=1000
RUN addgroup --gid ${GID} ${USER} \
 && adduser \
    --disabled-password \
    --gecos ${USER} \
    --gid ${GID} \
    --uid ${UID} \
    ${USER}

ARG APP_DIR=/home/${USER}/app
RUN mkdir -p ${APP_DIR} \
 && chown ${UID}:${GID} ${APP_DIR}

WORKDIR ${APP_DIR}
# COPY --chown=${UID}:${GID} Pipfile Pipfile.lock ./
# RUN pipenv install --system --deploy --ignore-pipfile --dev

COPY --chown=${UID}:${GID} . .
RUN pip install -e .

USER ${USER}
ENV SHELL /bin/bash