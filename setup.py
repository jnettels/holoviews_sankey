"""Define setup for the package ``holoviews_sankey``."""
from setuptools import setup
from setuptools_scm import get_version


try:
    version = get_version(version_scheme='post-release')
except LookupError:
    version = '0.0.0'
    print('Warning: setuptools-scm requires an intact git repository to detect'
          ' the version number for this build.')

setup(name='holoviews_sankey',
      version=version,
      description='Plot sankey flowcharts from spreadheet data with holoviews',
      long_description=open('README.md').read(),
      license='MIT',
      author='Joris Zimmermann',
      author_email='joris.zimmermann@stw.de',
      url='https://github.com/jnettels/holoviews_sankey',
      python_requires='>=3.7',
      install_requires=[
          'pandas',
          'openpyxl',
          'bokeh',
          'holoviews',
          'selenium',
          'firefox',
          'geckodriver',
      ],
      packages=['holoviews_sankey'],
      package_data={
        'holoviews_sankey': ['examples/Sankey.xlsx'],
        },
      )
