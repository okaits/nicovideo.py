#!/bin/bash -e
export SPHINX_APIDOC_OPTIONS=members,show-inheritance
mkdir -p docs_build/{markdown,output}
python3 -m poetry run sphinx-apidoc -Fo ./docs_build/markdown nicovideo/
echo '
project = "nicovideo"
copyright = "2024, okaits#7534"
author = "okaits7534"
import os
import sys
sys.path.insert(0, os.path.abspath("../../nicovideo"))
extensions.append("sphinx.ext.napoleon")
extensions.append("sphinx_markdown_builder")
html_theme = "sphinx_rtd_theme"
'>>./docs/markdown/conf.py
python3 -m poetry sphinx-build -M markdown -a docs_build docs_build/output
