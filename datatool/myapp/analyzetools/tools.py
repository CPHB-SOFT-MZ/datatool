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
        # For each column of values we want the maximum of
        for value_header in value_headers:
            res_max = DataContainer()

            # narrow down the csv dataframe
            df = self.csv[info_headers + [value_header]]

            # returns a dataframe (only one row) of the index of what np.argmax returns
            value_pairs = df.ix[np.argmax(np.array(self.csv[value_header]))]

            # Add these headers to the res_max object
            res_max.value_headers = {value_header: value_pairs[value_header]}

            # Get all the info for that one row that was requested and append it to
            for info_header in info_headers:
                res_max.append_info_header(info_header, value_pairs[info_header])
            df_return.append(res_max)

        # Put the result into the parsed queue
        q.put(('amax', df_return))

    def bar_chart(self, q, value_header):
        print("Generating bar chart")
        bar = Bar(self.csv, label=value_header, title=value_header, plot_width=800, legend=False)
        q.put(('bar', bar))

    def histogram(self, q, value_header, label_header=None):
        print("Generating histogram")
        if label_header is not None:
            q.put(('hist',
                   Histogram(self.csv, label=label_header, values=value_header, title=value_header, plot_width=800,
                             legend=False)))
        else:
            q.put(('hist', Histogram(self.csv, values=value_header, title=value_header, plot_width=800, legend=False)))

    # Finds the row with minimum value for each value header and returns the value and all requested info headers
    def minimum_value(self, q, value_headers, info_headers):
        print("Generating min value")
        df_return = []

        # For each column of values we want the minimum of
        for value_header in value_headers:
            res_min = DataContainer()

            # narrow down the csv dataframe
            df = self.csv[info_headers + [value_header]]

            # returns a dataframe (only one row) of the index of what np.argmin returns
            value_pairs = df.ix[np.argmin(np.array(self.csv[value_header]))]

            # Add these headers to the res_min object
            res_min.value_headers = {value_header: value_pairs[value_header]}

            # Get all the info for that one row that was requested and append it to
            for info_header in info_headers:
                res_min.append_info_header(info_header, value_pairs[info_header])
            df_return.append(res_min)
        # Put the result into the parsed queue
        q.put(('amin', df_return))

    def median_value_for(self, q, value_headers, group_by):
        # df_return = []
        # for value_header in value_headers:
        #     res_medi = DataContainer()
        #
        #     df = self.csv[info_headers + [value_header]]
        #
        #     values = self.csv[value_header]
        #     median = np.median(np.array(values))
        #     value_pairs = df.ix[np.argwhere(median==values)]
        #     res_medi.value_header = {value_header: value_pairs[value_header]}
        #     for info_header in info_headers:
        #         res_medi.append_info_header(info_header, value_pairs[info_header])
        #     df_return.append(res_medi)
        # q.put(('median', df_return))
        df_return = []
        csv = self.csv
        uniques = np.unique(self.csv[group_by])

        # For every
        for unique in uniques:
            res_med = DataContainer()
            res_med.info_headers.update({group_by: unique})
            for value_header in value_headers:
                data = csv[(csv[group_by] == unique)][[value_header] + [group_by]]
                avg = np.nanmedian(data[value_header])
                res_med.append_value_header(value_header, avg)
            df_return.append(res_med)

        q.put(('med_for', df_return))

    # TODO: Needs to be rewritten after a test has been written and run
    def average_value(self, q, value_headers):
        values = []
        for value_header in value_headers:
            res_avg = DataContainer()
            avg = np.average(np.array(self.csv[value_header]))
            res_avg.value_headers = {value_header: avg}
            values.append(res_avg)
        q.put(('avg', values))

    def average_value_for(self, q, value_headers, group_by):
        df_return = []
        csv = self.csv
        uniques = np.unique(self.csv[group_by])

        # For every unique value of the requested group_by column
        for unique in uniques:
            res_avg = DataContainer()
            res_avg.info_headers.update({group_by: unique})

            for value_header in value_headers:
                # The data we want to find the average of.
                # Though only for the uniques
                data = csv[(csv[group_by] == unique)][[value_header] + [group_by]]

                # Calculate the average of the column of our value_header
                avg = np.nanmean(data[value_header])
                res_avg.append_value_header(value_header, avg)
            df_return.append(res_avg)
        # Put our result into our queue
        q.put(('avg_for', df_return))

    def sum(self, q, value_headers):
        values = []
        for value_header in value_headers:
            res_sum = DataContainer()
            sum = np.sum(np.array(self.csv[value_header]))
            res_sum.value_headers = {value_header: sum}
            values.append(res_sum)
        q.put(('sum', values))

    def occurences(self, q, value_headers):
        tuple_list = []
        for value_header in value_headers:
            res_occ = DataContainer()
            array = np.array(self.csv[value_header])
            info, count = np.unique(array, return_counts=True)
            res = zip(info, count)
            for r in res:
                res_occ.info_headers.update({r[0]: r[1]})
            tuple_list.append(res_occ)
        q.put(('occur', tuple_list))
