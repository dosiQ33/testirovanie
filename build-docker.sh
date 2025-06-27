#!/bin/bash

# docker compose down
docker compose -f docker-compose.prod.yml build
docker save coc_back  | gzip > coc_back.tar.gz
