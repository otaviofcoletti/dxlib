# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

project = "dxlib"
copyright = "2023, Rafael Zimmer"
author = "Rafael Zimmer"
release = "1.0.13"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.githubpages",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    # "sphinx_copybutton",
    'sphinx_exec_code',
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_title = 'dxlib'
html_theme = 'sphinxawesome_theme'
extensions += ["sphinxawesome_theme.highlighting"]
html_static_path = ["_static"]
html_favicon = "_static/favicon.ico"
html_sidebars = {
    '**': [
        'globaltoc.html',
    ],
}

exec_code_working_dir = '../..'
