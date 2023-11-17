#!/bin/bash

USER_ID=$(id -u)
GROUP_ID=$(id -g)

# For Rootless Docker
if [ -n "$(docker info 2>&1 | grep 'rootless')" ]; then
  ROOTLESS=true
  # Add rootless-docker group
  SUBGID=`grep "^${USER}:" /etc/subgid | grep -oE ":[0-9]+:" | sed "s/://g"`
  CONTAINER_GID=$(( $SUBGID + $USER_ID - 1 ))
  
  # Check group already exists
  if [ -z "$(grep -E "^[^:]+:[^:]+:$CONTAINER_GID:" /etc/group)" ]; then
    echo "Create Rootless-docker group"
    GNAME=rootless-$USER
    sudo groupadd -g $CONTAINER_GID $GNAME
  else
    GNAME=`grep -E "^[^:]+:[^:]+:$CONTAINER_GID:" /etc/group | grep -oE "^[^:]+"`
  fi
  if [ -z "$(id -G | grep $CONTAINER_GID)" ]; then
    echo "Add Rootless-docker group to use docker bind mount."
    sudo gpasswd -a $USER $GNAME
  fi
else
  ROOTLESS=false
fi

ROOT=$(cd $(dirname $0); pwd)
ProjName=${ROOT##*/}

# Generate .env file
echo "Setting UID, GID and Project name."
echo "UID=$USER_ID" > $ROOT/.env
echo "GID=$GROUP_ID" >> $ROOT/.env
echo "COMPOSE_PROJECT_NAME=${ProjName,,}" >> $ROOT/.env

# Initial setting
if [ -z "$(docker volume ls -q -f name='renv')" ]; then
  echo "Create renv volume."
  docker volume create renv
fi

