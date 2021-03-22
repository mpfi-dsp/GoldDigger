#!/usr/bin/env bash

CONFIG_VAR="$(python -c 'import config;print(config.LOCAL_IMAGE_FOLDER)')"
echo $CONFIG_VAR