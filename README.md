Holoviews Sankey
================

This script uses holoviews and bokeh to create sankey flowcharts
from input data and save them as png, svg and html.

It can be used via the commandline (run with ``--help`` to see
all the arguments) or by calling the function ``create_and_save_sankey()``
from another script.

Example usage:
```
python -m holoviews_sankey --help
python -m holoviews_sankey --file .\Sankey.xlsx --sheets "Example A" "Example C" -o ".\custom\output\path"
python -m holoviews_sankey --file .\Sankey.xlsx --width 1000  --label_text_font_size 8pt
python -m holoviews_sankey --file .\Sankey.xlsx --width 1000  --label_text_font_size 8pt --unit MWh --sheets Sheet1 --decimals 2 --node_width 10  --language en_en
```