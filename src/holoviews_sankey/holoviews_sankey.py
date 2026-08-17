# MIT License

# Copyright (c) 2022 Joris Zimmermann

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

"""Create png, svg and html sankey flowcharts from tabular data.

Create a ``Sankey`` plot as png, svg and html with data from an Excel file.
Uses ``Sankey.xlsx`` in the same directory per default, but can be started
from the command line to load any other file. One Sankey is created for
each sheet in the Excel file.

For more info on creating Sankeys with HoloViews, see
http://holoviews.org/reference/elements/bokeh/Sankey.html

Usage
----

You may want to run this script directly and adapt the main method, or
import it from somewhere else and just use ``create_and_save_sankey()``.

Alternatively, you can run this script from the command line like this:

.. code::

    python -m holoviews_sankey --file 'Sankey.xlsx' --sheets "Example A" "Example B"


See the help to show all arguments:

.. code::

    python -m holoviews_sankey --help

"""

import sys
import os
from shutil import which
import logging
import argparse
import inspect
import locale
import holoviews as hv
from bokeh.io import export_png, export_svgs, show, output_file, webdriver
from bokeh.layouts import gridplot

# Define the logging function
logger = logging.getLogger(__name__)


def include_firefox_and_geckodriver_in_path():
    """Add firefox and geckodriver executables to PATH.

    In some conda environments, those paths were not properly defined
    in PATH and could not be found by selenium (used for png export).

    If firefox and geckodriver are found in PATH, nothing is changed.
    """
    PATH = os.environ['PATH'].split(os.pathsep)
    if which("firefox") is None:
        PATH.append(
            os.path.join(os.path.dirname(sys.executable), 'Library', 'bin'))
    if which("geckodriver") is None:
        PATH.append(
            os.path.join(os.path.dirname(sys.executable), 'Scripts'))
    os.environ['PATH'] = os.pathsep.join(PATH)


def create_sankeys_from_dict(df_dict, file, output_dir, **kwargs):
    """Create sankey plots from a dictionary of DataFrames."""
    sankey_list = []
    for sheet_name, df in df_dict.items():
        logger.info(sheet_name)
        if logger.isEnabledFor(logging.INFO):
            print(df)  # Show imported DataFrame on screen

        # Use same name as input file, plus sheet_name
        filename = os.path.join(
            output_dir,
            os.path.splitext(
                os.path.basename(file))[0]+' '+str(sheet_name))

        try:
            # Create the plot figure from DataFrame
            bkplot = create_and_save_sankey(df, filename, sheet_name, **kwargs)
            sankey_list += [bkplot]  # Add result to list of sankeys

        except Exception as ex:
            logger.exception(ex)
            logger.error("%s: %s", sheet_name, ex)

    # Create html output
    output_file(os.path.join(output_dir,
                             os.path.splitext(
                                 os.path.basename(file))[0] + '.html'),
                title=os.path.splitext(file)[0])
    bokeh_grid = gridplot(sankey_list, ncols=1, sizing_mode='stretch_width')
    show(bokeh_grid)

    return True


def create_and_save_sankey(edges, filename=None, title='', title_html='',
                           edge_color_index='To', show_plot=False,
                           palette=None, decimals=2, unit='',
                           width=1400, height=600,
                           fontsize=11, label_text_font_size='17pt',
                           node_width=45, node_padding=10, export_title=False,
                           toolbar_location=None, title_max_chars=None):
    """Use HoloViews to create a Sankey plot from the input data.

    This is the recommended function to implement into other Python scripts.

    Args:
        edges (DataFrame): Pandas DataFrame with columns 'From', 'To' and
        'Value'. Names are arbitrary, but must match ``edge_color_index``.

        filename (str): Filename (without extension) of exported png and svg.

        title (str): Diagram title for html output.

        export_title (bool, optional): If true, title is shown on each plot.

        edge_color_index (str, optional): Name of column to use for edge
        color. With 'To', all edges arriving at a node have the same color.
        Defaults to 'To'.

        palette (list or dict, optional): List or dictionary of colors related
        to entries in edges DataFrame. If dictionary, all undefined entries
        will be grey.

        title_max_chars (int, optional): Number of characters to keep in the
        title, to fit onto the image. Otherwise a .svg file might not be
        usable in MS Word.

        Other arguments show inputs for ``hv.Sankey().options()``

    Returns:
        bkplot (object): The Bokeh plot object.

    """
    try:
        # If export_png or export_svgs are called repeatedly, by default
        # a new webdriver is created each time. For me, on Windows, those
        # webdrivers survive the script and the processes keep running
        # in task manager.
        # A solution is to manually define a webdriver that we can actually
        # close automatically:
        include_firefox_and_geckodriver_in_path()
        web_driver = webdriver.create_firefox_webdriver()
    except Exception as ex:
        logger.exception(ex)
        web_driver = None

    hv.extension('bokeh')  # Some HoloViews magic to make it work with Bokeh

    # Define a custom color palette
    if palette is None:
        palette = ['#f14124', '#ff8021', '#e8d654', '#5eccf3', '#b4dcfa',
                   '#4e67c8', '#56c7aa', '#24f198', '#2160ff', '#c354e8',
                   '#e73384', '#c76b56', '#facdb4']
    # Alternative: Dictionary of colors related to entries in edges DataFrame.
    # All undefined entries will be grey.
    # palette = {'A': '#f14124', 'B': '#ff8021', 'C': '#e8d654',
    #            'D': '#5eccf3', 'E': '#b4dcfa', 'F': '#4e67c8',
    #            'G': '#56c7aa', 'H': '#24f198', 'I': '#2160ff',
    #            'J': '#c354e8', 'K': '#e73384', 'L': '#c76b56',
    #            'M': '#facdb4',
    #            'X': '#5eccf3', 'Y': '#b4dcfa', 'Z': '#4e67c8',
    #            }

    # Only keep non-zero rows (flow with zero width cannot be plotted)
    edges = edges.loc[(edges != 0).all(axis=1)]

    def fmt(x):
        """Format the Sankey diagram values."""
        if decimals is not None:
            x = round(x, decimals)
        if decimals is None and unit is None:
            return x
        elif decimals is None:
            return f'{x} {unit}'
        else:
            # return f'{round(x, decimals)} {unit}'
            return f'{x:n} {unit}'  # use locale setting for decimal sign

    # Use HoloViews to create the plot
    hv_sankey = hv.Sankey(edges,
                          vdims=hv.Dimension('Value', value_format=fmt)
                          ).options(
        width=width,
        height=height,
        edge_color_index=edge_color_index,
        cmap=palette,
        edge_cmap=palette,
        node_width=node_width,  # default 15
        fontsize=fontsize,
        label_text_font_size=label_text_font_size,
        node_padding=node_padding,  # default 10
        )

    # HoloViews is mainly used for creating html content. Getting the simple
    # PNG is a little more involved
    hvplot = hv.plotting.bokeh.BokehRenderer.get_plot(hv_sankey)
    bkplot = hvplot.state
    bkplot.toolbar_location = toolbar_location  # disable Bokeh toolbar
    bkplot.toolbar.active_drag = None  # disable pan/drag
    bkplot.toolbar.active_scroll = None  # disable scroll

    if export_title is True:  # Add the title to the file export
        bkplot.title.text = str(title)

        if title_max_chars is not None:
            # Only keep the first X characters to fit onto the image
            # Otherwise a .svg might not be usable in MS Word!
            bkplot.title.text = bkplot.title.text[:title_max_chars]

    if filename is not None:
        # Create the output folder, if it does not already exist
        if not os.path.exists(os.path.abspath(os.path.dirname(filename))):
            os.makedirs(os.path.abspath(os.path.dirname(filename)))

        try:
            export_png(bkplot, filename=filename+'.png', webdriver=web_driver)
        except Exception as e:
            logger.exception(e)
        try:
            bkplot.output_backend = 'svg'
            export_svgs(bkplot, filename=filename+'.svg', webdriver=web_driver)
        except Exception as e:
            logger.exception(e)

    if web_driver is not None:
        web_driver.quit()  # Quit webdriver after finishing using it

    # For html output
    bkplot.title.text = str(title)
    bkplot.sizing_mode = 'stretch_width'

    if filename is not None:
        if title_html == '':
            title_html = title
        # Create html output
        output_file(filename + '.html', title=title_html)

    if show_plot:
        show(bkplot)

    return bkplot


def setup(log_level='INFO', language='de_DE.UTF-8'):
    """Set up the logger."""
    logger.setLevel(level=log_level.upper())  # Logger for this module
    logging.getLogger('holoviews').setLevel(level='ERROR')
    logging.basicConfig(format='%(asctime)-15s %(levelname)-8s %(message)s')

    # Define language for formating decimal sign of floats
    locale.setlocale(locale.LC_ALL, language)


def run_option_parser(file=None, sheets=None, output_dir='./out',
                      log_level='INFO', language='de_DE.UTF-8'):
    """Define and run the argument parser. Return the chosen file path."""
    description = 'Plot a Sankey chart from an Excel spreadheet.'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.
                                     ArgumentDefaultsHelpFormatter)

    parser.add_argument('-f', '--file', dest='file', help='Path to an Excel '
                        'spreadsheet.', type=str, required=True)
    parser.add_argument('-s', '--sheets', dest='sheets', nargs='+',
                        help='List of sheets in the file to process (use all '
                        'sheets if not defined).', default=sheets)
    parser.add_argument('-o', '--output_dir', dest='output_dir',
                        help='Directory to use for the output.',
                        type=str, default=output_dir)
    parser.add_argument('-l', '--log_level', dest='log_level',
                        help='Define the log level', type=str,
                        default=log_level)
    parser.add_argument('--language', dest='language',
                        help='Define the language for number formats, e.g.'
                        '"en_en" or "de_de"',
                        type=str, default=language)

    sig = inspect.signature(create_and_save_sankey)
    for name, param in sig.parameters.items():
        if param.name in ['edges', 'filename', 'title']:
            continue
        parser.add_argument('--{}'.format(param.name), dest=param.name,
                            default=param.default, help='Other sankey setting',
                            type=type(param.default))

    args = parser.parse_args()
    return args
