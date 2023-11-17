FROM python:3.11.6 as python

WORKDIR /

RUN pip install -U pip \
    && pip install pipenv \
    isort

FROM r-base:4.2.1

ARG UID=1000
ARG GID=1000
ARG PSWD=pswd
ARG PY_VER=3

ENV USERID ${UID}
ENV GROUPID ${GID}
ENV PASSWORD ${PSWD}
ENV PYTHON_VER ${PY_VER}

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    sudo \
    git \
    openssh-server \
    libxml2-dev \
    && apt-get clean \
    && GROUP=`grep -E "^[^:]+:[^:]+:${GID}:" /etc/group` || true \
    && if [ -z "${GROUP}" ]; then groupadd -g ${GID} container-group; fi \
    && usermod -u ${UID} -g ${GID} docker \
    && gpasswd -a docker sudo \
    && echo "docker ALL=(ALL) ALL" >> /etc/sudoers \
    && echo "docker:${PSWD}" | chpasswd \
    && rm /var/log/apt/history.log

COPY --from=python /usr/local/bin /usr/local/bin
COPY --from=python /usr/local/lib /usr/local/lib
COPY --from=python /usr/local/include /usr/local/include

USER docker

RUN mkdir -p ~/.cache/R/renv ~/library

WORKDIR /home/docker/workspace

CMD bash ~/workspace/.build/container.sh
