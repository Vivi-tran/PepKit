#!/bin/bash 
flake8 . \
  --count \
  --max-complexity=13 \
  --max-line-length=120 \
  --statistics