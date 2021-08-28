"""Sphinx configuration."""
from datetime import datetime

html_title = "Hopscotch"
project = "Hopscotch"
author = "Paul Everitt"
copyright = f"{datetime.now().year}, {author}"
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]
autodoc_typehints = "description"
html_theme = "furo"
myst_enable_extensions = ["colon_fence"]
