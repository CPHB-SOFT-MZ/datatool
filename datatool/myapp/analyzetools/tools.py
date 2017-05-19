import pandas as pd
import numpy as np
from bokeh.embed import components
from bokeh.io import output_file, show
from bokeh.plotting import figure
from bokeh.charts import Histogram, Bar


class Tools:
    def __init__(self):
        self.csv = pd.DataFrame()

    def set_csv(self, csv):
        self.csv = csv

    # Finds the row with maximum value for each value header and returns the value and all requested info headers
    def maximum_value(self, value_headers, info_headers):
        df_return = []
        index = 0
        for value_header in value_headers:

            #df_return.update({value_header})
            df = self.csv[info_headers + [value_header]]

            value_pairs = df.ix[np.argmax(np.array(self.csv[value_header]))]
            df_return.append({'info_headers': {},
                              'value_header': {value_header: value_pairs[value_header]}
                              })
            for info_header in info_headers:
                df_return[index]['info_headers'].update({info_header: value_pairs[info_header]})
            index = index + 1

        return df_return

    def bar_chart(self, value_header):
        p = Bar(self.csv[value_header], label=value_header, title=value_header)
        return p
