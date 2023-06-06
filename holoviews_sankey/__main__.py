"""Provide a __main__ entry point for the holoviews_sankey package."""
import pandas as pd
from holoviews_sankey import setup, run_option_parser, create_sankeys_from_dict


def main():
    """Run the the option parser and create sankey based on the input."""
    # Run the comand line option parser
    args = run_option_parser()
    # Store the results, while removing the used arguments
    # The remaining arguments will be handed to hv.Sankey().options()
    file_load = args.__dict__.pop('file')
    sheets = args.__dict__.pop('sheets')
    output_dir = args.__dict__.pop('output_dir')
    setup(args.__dict__.pop('log_level'),
          args.__dict__.pop('language')
          )  # Perform some setup stuff

    # Read in data as Pandas DataFrame (file name can be given via parser)
    df_dict = pd.read_excel(file_load, header=0, sheet_name=sheets)

    # Try to create sankey for each sheet in the workbook
    create_sankeys_from_dict(df_dict, output_dir, file_load, **args.__dict__)


if __name__ == '__main__':
    main()
