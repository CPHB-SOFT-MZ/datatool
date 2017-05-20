import pandas as pd
import numpy as np
from bokeh.charts import Histogram, Bar

from datatool.myapp.analyzetools.customObjects import DataContainer


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
            res_max = DataContainer()

            df = self.csv[info_headers + [value_header]]

            value_pairs = df.ix[np.argmax(np.array(self.csv[value_header]))]
            res_max.value_header = {value_header: value_pairs[value_header]}

            for info_header in info_headers:
                res_max.append_info_header(info_header, value_pairs[info_header])
            df_return.append(res_max)
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

    # Finds the row with minimum value for each value header and returns the value and all requested info headers
    def minimum_value(self, value_headers, info_headers):
        df_return = []
        for value_header in value_headers:
            df = self.csv[info_headers + [value_header]]
            df_return.append(df.ix[np.argmin(np.array(self.csv[value_header]))])
        return df_return

    def median_value(self, value_headers, info_headers):
        df_return = []
        for value_header in value_headers:
            df = self.csv[info_headers + [value_header]]
            values = self.csv[value_header]
            median = np.median(np.array(values))
            df_return.append(df.ix[np.argwhere(median==values)])
        return df_return

    def average_value(self, value_headers, info_headers):
        df_return = []
        for value_header in value_headers:
            df = self.csv[info_headers + [value_header]]
            values = self.csv[value_header]
            average = np.average(np.array(values))
            df_return.append(df.ix[np.argwhere(average==values)])
        return df_return

    def mean_value(self, value_headers, info_headers):
        df_return = []
        for value_header in value_headers:
            df = self.csv[info_headers + [value_header]]
            values = self.csv[value_header]
            mean = np.mean(np.array(values))
            df_return.append(df.ix[np.argwhere(mean==values)])
        return df_return

    def sum(self, value_headers, info_headers):
        values = []
        for value_header in value_headers:
            sum = np.sum(np.array(self.csv[value_header]))
            values.append(sum)
        return values

    def unique_count(self, value_headers, info_headers):
        tuple_list = []
        for value_header in value_headers:
            array = np.array(self.csv[value_header])
            info, count = np.unique(array, return_counts=True)
            tuple_list.append(zip(info, count))
        return tuple_list
