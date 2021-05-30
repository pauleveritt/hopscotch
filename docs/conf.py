"""Sphinx configuration."""
from datetime import datetime


project = "Hopscotch"
author = "Paul Everitt"
copyright = f"{datetime.now().year}, {author}"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]
autodoc_typehints = "description"
html_theme = "furo"
