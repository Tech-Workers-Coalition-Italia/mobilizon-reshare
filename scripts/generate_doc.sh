#!/bin/bash
export SECRETS_FOR_DYNACONF='mobilizon_reshare/.secrets.toml'
poetry run sphinx-apidoc -f -o api_documentation/source/ mobilizon_reshare/
cd api_documentation 
poetry run make html
if [ -z $1 ] || [[ $1 != 'nox' ]]
then
#	xdg-open build/html/index.html
	firefox build/html/index.html
fi
cd ..
