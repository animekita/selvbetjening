#!/bin/bash

BASEPATH=$(cd "$(dirname "$0")/.."; pwd)

cd $BASEPATH
./manage.py dumpdata --indent=2 user members events mailcenter auth.Group > sdemo/fixtures/sdemo-example-site.json