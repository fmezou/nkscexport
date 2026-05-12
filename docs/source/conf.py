# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
from pathlib import Path

# Python files and docs are in sperate folder, so source path is added
sys.path.insert(0, str(Path('..', '..', 'src').resolve()))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
# Import project information from the main script
from nkscexport import __project__
from nkscexport import __copyright__
from nkscexport import __author__
from nkscexport import __version__
from nkscexport import __release__
project = __project__
copyright = __copyright__
author = __author__
release = __release__
version = __version__

# General configuration --------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
needs_sphinx = '8.1'
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.napoleon",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.graphviz",
    "sphinx_rtd_theme"
]
# -- Options for highlighting --------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-highlighting
pygments_style = "sphinx"

# -- Options for markup --------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-markup
show_authors = False

# -- Options for object signatures ---------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-object-signatures
add_function_parentheses = True

# -- Options for source files --------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-source-files
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for templating ----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-templating
templates_path = ["_templates"]

# Builder options --------------------------------------------------------------
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = "sphinx_rtd_theme"
# -- Theme options
#  https://pypi.org/project/sphinx-rtd-theme/
html_theme_options = {
#    "github_url" : "https://github.com/fmezou/nkscexport"
}
html_static_path = ["_static"]
html_show_sourcelink = False

# Extension options -----------------------------------------------------------
# -- Options for sphinx.ext.intersphinx----------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
# Locations and names of other projects that should be linked to in this
# documentation.
# Add links to modules and objects in the Python standard library documentation.
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

# -- Options for sphinx.ext.napoleon ------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
napoleon_google_docstring = True
napoleon_numpy_docstring = False

# -- Options "sphinx.ext.autodoc" ---------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
autodoc_member_order = "groupwise"

# -- Options "sphinx.ext.graphviz" --------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/graphviz.html
graphviz_output_format = "svg"

# -- Options "sphinx.ext.todo"-------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html
todo_include_todos = True
