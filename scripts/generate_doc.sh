#!/bin/sh
export SECRETS_FOR_DYNACONF='mobilizon_reshare/.secrets.toml'
poetry run sphinx-apidoc -f -o api_documentation/source/ mobilizon_reshare/
cd api_documentation 
poetry run make html
cd ..
