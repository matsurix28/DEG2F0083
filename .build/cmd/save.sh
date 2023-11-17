#!/bin/bash

if [ -f /var/apt/history.log ]; then
  APTS=`grep "install" /var/log/apt/history.log | sed "s/^.* install //g" | sed -z "s/\n/ /g" | \
  awk '{for(i=1; i<=NF; i++) {if($i !~ /^-/) {if($i ~ /=/) {print substr($i,1,index($i,"=")-1)} else {print $i}}}}'`

  dpkg -l $APTS | grep "^ii" | awk '{print $2"="$3}' > /home/docker/workspace/.build/apt_packages.txt
fi

cd ~/workspace
R -q -e "renv::install(); renv::snapshot()"