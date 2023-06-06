# Copyright (C) 2020 Joris Zimmermann

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see https://www.gnu.org/licenses/.

"""Define tests to run during build process."""
import unittest
import os
import pkg_resources  # requires setuptools
import pandas as pd

from holoviews_sankey import setup, run_option_parser, create_sankeys_from_dict


def main_test():
    """Run the regular main method with an example input file."""
    # Get example user input. Directory is different in conda test environment
    file = os.path.join(os.path.dirname(__file__), 'examples', 'Sankey.xlsx')
    if not os.path.exists(file):
        file = os.path.relpath(os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '..', 'holoviews_sankey', 'examples', 'Sankey.xlsx')))

    # Run the comand line option parser
    args = run_option_parser(file_default=file)
    # Store the results, while removing the used arguments
    # The remaining arguments will be handed to hv.Sankey().options()
    file_load = args.__dict__.pop('file')
    sheets = args.__dict__.pop('sheets')
    output_dir = args.__dict__.pop('output_dir')
    setup(args.__dict__.pop('log_level'),
          args.__dict__.pop('language')
          )  # Perform some setup stuff

    # Read in data as Pandas DataFrame (file name can be given via parser)
    # For the 'noarch' conda build, the following file has to be accessed
    # not from a regular file path, but as a pkg resources object
    with pkg_resources.resource_stream('holoviews_sankey', file_load) as path:
        df_dict = pd.read_excel(path, header=0, sheet_name=sheets)

    # Try to create sankey for each sheet in the workbook
    create_sankeys_from_dict(df_dict, output_dir, file_load, **args.__dict__)

    return True


class TestMethods(unittest.TestCase):
    """Defines tests."""

    def test(self):
        """Test the main method of the script."""
        self.assertTrue(main_test())


if __name__ == '__main__':
    unittest.main()
