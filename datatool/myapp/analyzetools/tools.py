import pandas as pd
import numpy as np
from bokeh.embed import components
from bokeh.io import output_file, show
from bokeh.plotting import figure
from bokeh.charts import Histogram, Bar

from datatool.myapp.analyzetools.customObjects import Maximum


class Tools:
    def __init__(self):
        self.csv = pd.DataFrame()

    def set_csv(self, csv):
        self.csv = csv

    # Finds the row with maximum value for each value header and returns the value and all requested info headers
    def maximum_value(self, value_headers, info_headers):
        df_return = []
        for value_header in value_headers:
            ret_max = Maximum()

            df = self.csv[info_headers + [value_header]]

            value_pairs = df.ix[np.argmax(np.array(self.csv[value_header]))]
            ret_max.value_header = {value_header: value_pairs[value_header]}

            for info_header in info_headers:
                ret_max.append_info_header(info_header, value_pairs[info_header])
            df_return.append(ret_max)
        return df_return

    def bar_chart(self, value_header):
        p = Bar(self.csv[value_header], label=value_header, title=value_header, plot_width=800)
        return p


    def histogram(self, value_header, label_header=None):
        p = None
        if label_header != None:
            p = Histogram(self.csv, label=label_header, values=value_header, title=value_header, plot_width=800)
        else:
            p = Histogram(self.csv, values=value_header, title=value_header, plot_width=800)
        return p
