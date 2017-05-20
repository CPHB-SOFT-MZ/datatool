import pandas as pd
import numpy as np
from bokeh.charts import Histogram, Bar

from datatool.myapp.analyzetools.customObjects import Maximum


class Tools:

    def __init__(self):
        self.csv = pd.DataFrame()

    def set_csv(self, csv):
        self.csv = csv

    # Finds the row with maximum value for each value header and returns the value and all requested info headers
    def maximum_value(self, q, value_headers, info_headers):
        print("Generating max value")
        df_return = []
        for value_header in value_headers:
            ret_max = Maximum()

            df = self.csv[info_headers + [value_header]]

            value_pairs = df.ix[np.argmax(np.array(self.csv[value_header]))]
            ret_max.value_header = {value_header: value_pairs[value_header]}

            for info_header in info_headers:
                ret_max.append_info_header(info_header, value_pairs[info_header])
            df_return.append(ret_max)
        q.put(('amax', df_return))

    def bar_chart(self, q, value_header):
        print("Generating bar chart")
        bar = Bar(self.csv, label=value_header, title=value_header, plot_width=800, legend=False)
        q.put(('bar', bar))


    def histogram(self, q, value_header, label_header=None):
        print("Generating histogram")
        if label_header is not None:
            q.put(('hist', Histogram(self.csv, label=label_header, values=value_header, title=value_header, plot_width=800, legend=False)))
        else:
            q.put(('hist', Histogram(self.csv, values=value_header, title=value_header, plot_width=800, legend=False)))

