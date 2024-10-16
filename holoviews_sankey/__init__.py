"""Create png, svg and html sankey flowcharts from tabular data."""
from importlib.metadata import version, PackageNotFoundError

try:
    dist_name = 'holoviews_sankey'
    # Try to get the version name from the installed package
    __version__ = version(dist_name)
except PackageNotFoundError:
    try:
        # If package is not installed, try to get version from git
        from setuptools_scm import get_version
        __version__ = get_version(version_scheme='post-release',
                                  root='..', relative_to=__file__)
    except (LookupError, Exception) as e:
        print(e)
        __version__ = '0.0.0'

from .holoviews_sankey import *
