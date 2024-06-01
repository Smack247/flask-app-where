#!/bin/bash

mkdir -p functions
pip install -r requirements.txt -t functions/
cp -R . functions/
cd functions
zip -r app.zip *
mv app.zip ../functions/app.zip
cd ..

