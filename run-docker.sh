#!/bin/bash

cat coc_back.tar.gz | docker load
docker compose down
docker compose up -d