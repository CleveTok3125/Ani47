#!/bin/bash
pyinstaller main.spec
cp config.ini "./dist/Ani47/"
cp README.md "./dist/Ani47/"
cp LICENSE "./dist/Ani47/"