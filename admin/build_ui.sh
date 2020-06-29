#!/bin/bash

cd ../admin-ui

yarn build:prod

rsync -avzh --delete dist ../admin/

cd ../admin
