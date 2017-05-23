import pandas as pd
import numpy as np
from bokeh.charts import Histogram, Bar, Donut, Scatter
from bokeh.plotting import figure
import matplotlib.pyplot as plt, mpld3
import random

from datatool.datatool.analyzetools.customObjects import DataContainer


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
        bar = Bar(self.csv, label=value_header, title=value_header, plot_width=970, legend=False)
        q.put(('bar', bar))

    def bar_chart_sum(self, q, value_header, group_by):
        print("Generating bar char with sum")
        bar = Bar(self.csv, group_by, values=value_header, legend=False, plot_width=970)
        q.put(('bar_sum', bar))

    def histogram(self, q, value_header, label_header=None):
        print("Generating histogram")
        if label_header is not None:
            q.put(('hist',
                   Histogram(self.csv, label=label_header, values=value_header, title=value_header, plot_width=970,
                             legend=False)))
        else:
            q.put(('hist', Histogram(self.csv, values=value_header, title=value_header, plot_width=970, legend=False)))

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

    def occurrences(self, q, value_headers):
        tuple_list = []
        for value_header in value_headers:
            res_occ = DataContainer()
            array = np.array(self.csv[value_header])
            info, count = np.unique(array, return_counts=True)
            res = zip(info, count)
            for r in res:
                res_occ.append_value_header(r[0], r[1])
            res_occ.info_headers.update({value_header: ""})
            tuple_list.append(res_occ)
        q.put(('occur', tuple_list))

    def donut_chart(self, q, group_by):
        print("Baking donut...")
        #donut_chart = Donut(self.csv, label=group_by)
        #q.put(('donut', donut_chart))
        labels, counts = np.unique(np.array(self.csv[group_by]), return_counts=True)

        #Calculate the percentages and populate the array
        percentages = [(count * 100) / np.sum(counts) for count in counts]

        fig1, ax1 = plt.subplots()
        ax1.pie(percentages, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
        ax1.axis('equal')

        q.put(('donut', mpld3.fig_to_html(fig1)))

    def scatter_chart(self, q, x_label, y_label):
        print("Generating scatter markers")
        scatter_chart = Scatter(self.csv, x=x_label, y=y_label, title=x_label + " vs " + y_label,
                    xlabel = x_label, ylabel = y_label)
        q.put(('scatter', scatter_chart))

    def scatter_chart_grouped(self, q, x_label, y_label, grouped_by):
        # uniques = np.unique(np.array(self.csv[grouped_by]))
        #
        # scatter_chart = figure()
        # for un in uniques:
        #
        #     ccc = self.csv[(self.csv[grouped_by] == un)]
        #     print(un)
        #     r = lambda: random.randint(0, 255)
        #     scatter_chart.scatter(ccc[x_label], ccc[y_label], color='#%02X%02X%02X' % (r(),r(),r()),
        #                          alpha=0.5, line_color=None, size=10)
        print("Generating scatter markers")
        scatter_chart = Scatter(self.csv, x=x_label, y=y_label, color=grouped_by,
                                title=x_label + " vs " + y_label + " (shaded by " + grouped_by +")" ,
                                xlabel=x_label, ylabel=y_label)
        q.put(('scatter_group', scatter_chart))

    def line_graph(self, q, x, y, label_header):
        print("Generating line graph")
        if label_header is not None:
            p = figure(plot_width=400, plot_height=400, label=label_header)
            p.line(x, y, line_width=2)
            q.put(p)
        else:
            p = figure(plot_width=400, plot_height=400)
            p.line(x, y, line_width=2)
            q.put(p)

    def multiple_lines(self, q, list_of_lists, label_header):
        print("Generating multiple lines graph")
        if label_header is not None:
            p = figure(plot_width=400, plot_height=400, label=label_header)
            p.multi_line(list_of_lists, line_width=2)
            q.put(p)
        else:
            p = figure(plot_width=400, plot_height=400)
            p.multi_line(list_of_lists, line_width=2)
            q.put(p)

