#!/bin/bash

flake8 . --count --max-complexity=10 --max-line-length=90 \
	--per-file-ignores="test.py:F401. clustering.py:C901" \
	--exclude venv,__init__.py \
	--statistics