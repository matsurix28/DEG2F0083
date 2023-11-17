#!/bin/bash

echo $PASSWORD | sudo -S chown -R ${USERID}:${GROUPID} ~/workspace
umask 0002

ln -s ~/workspace/.build/.bashrc ~/.bashrc

while read line
do
    apt-get install -y $line
done < ~/workspace/.build/apt_packages.txt

R -q -e "renv::restore()"
pipenv sync
pipenv shell