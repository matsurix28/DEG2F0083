#!/bin/bash

while true; do
  R -e "renv::install('languageserver')" && break
done

while true; do
  R -e "renv::install('jsonlite')" && break
done
