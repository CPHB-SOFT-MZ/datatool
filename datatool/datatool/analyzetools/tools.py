import pandas as pd
import numpy as np
from bokeh.charts import Histogram, Bar, Donut, Scatter, Line
from bokeh.embed import components
import matplotlib.pyplot as plt, mpld3

from datatool.datatool.analyzetools.customObjects import DataContainer


def convert_chart(result):
    script, div = components(result)
    return {'script': script, 'div': div}


# Finds the row with maximum value for each value header and returns the value and all requested info headers
def maximum_value(csv, value_headers, info_headers):
    print("Generating max value")
    df_return = []
    # For each column of values we want the maximum of
    for value_header in value_headers:
        res_max = DataContainer()

        # narrow down the csv dataframe
        df = csv[info_headers + [value_header]]

        # returns a dataframe (only one row) of the index of what np.argmax returns
        value_pairs = df.ix[np.argmax(np.array(csv[value_header]))]

        # Add these headers to the res_max object
        res_max.value_headers = {value_header: value_pairs[value_header]}

        # Get all the info for that one row that was requested and append it to
        for info_header in info_headers:
            res_max.append_info_header(info_header, value_pairs[info_header])
        df_return.append(res_max)

    # Put the result into the parsed queue
    return 'amax', df_return


def bar_chart(csv, value_header):
    print("Generating bar chart")
    bar = Bar(csv, label=value_header, title=value_header, plot_width=970, legend=False)
    return 'bar', convert_chart(bar)


def bar_chart_sum(csv, value_header, group_by):
    print("Generating bar char with sum")
    bar = Bar(csv, group_by, values=value_header, legend=False, plot_width=970)
    return 'bar_sum', convert_chart(bar)


def histogram(csv, value_header, label_header):
    print("Generating histogram")

    histo = Histogram(csv, label=label_header, values=value_header, title=value_header, plot_width=970,
                      legend=False)
    return 'hist', convert_chart(histo)


# Finds the row with minimum value for each value header and returns the value and all requested info headers
def minimum_value(csv, value_headers, info_headers):
    print("Generating min value")
    df_return = []

    # For each column of values we want the minimum of
    for value_header in value_headers:
        res_min = DataContainer()

        # narrow down the csv dataframe
        df = csv[info_headers + [value_header]]

        # returns a dataframe (only one row) of the index of what np.argmin returns
        value_pairs = df.ix[np.argmin(np.array(csv[value_header]))]

        # Add these headers to the res_min object
        res_min.value_headers = {value_header: value_pairs[value_header]}

        # Get all the info for that one row that was requested and append it to
        for info_header in info_headers:
            res_min.append_info_header(info_header, value_pairs[info_header])
        df_return.append(res_min)
    # Put the result into the parsed queue
    return 'amin', df_return


def median_value_for(csv, value_headers, group_by):
    df_return = []
    uniques = np.unique(csv[group_by])

    # For every
    for unique in uniques:
        res_med = DataContainer()
        res_med.info_headers.update({group_by: unique})
        for value_header in value_headers:
            data = csv[(csv[group_by] == unique)][[value_header] + [group_by]]
            avg = np.nanmedian(data[value_header])
            res_med.append_value_header(value_header, avg)
        df_return.append(res_med)

    return 'med_for', df_return


def average_value(csv, value_headers):
    values = []
    for value_header in value_headers:
        res_avg = DataContainer()
        avg = np.average(np.array(csv[value_header]))
        res_avg.value_headers = {value_header: avg}
        values.append(res_avg)
    return 'avg', values


def average_value_for(csv, value_headers, group_by):
    df_return = []
    uniques = np.unique(csv[group_by])

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
    return 'avg_for', df_return


def sums(csv, value_headers):
    values = []
    for value_header in value_headers:
        res_sum = DataContainer()
        sum = np.sum(np.array(csv[value_header]))
        res_sum.value_headers = {value_header: sum}
        values.append(res_sum)
    return 'sum', values


def occurrences(csv, value_headers):
    tuple_list = []
    for value_header in value_headers:
        res_occ = DataContainer()
        array = np.array(csv[value_header])
        info, count = np.unique(array, return_counts=True)
        res = zip(info, count)
        for r in res:
            res_occ.append_value_header(r[0], r[1])
        res_occ.info_headers.update({value_header: ""})
        tuple_list.append(res_occ)
    return 'occur', tuple_list

def pie_chart_alternative(csv, group_by):
    print("Baking pie...")
    d = Donut(csv, label=group_by)
    return 'pie', convert_chart(d)

def pie_chart(csv, group_by):
    print("Baking pie...")
    labels, counts = np.unique(np.array(csv[group_by]), return_counts=True)

    # Calculate the percentages and populate the array
    percentages = [(count * 100) / np.sum(counts) for count in counts]


    fig1, ax1 = plt.subplots()
    print("About to return")
    ax1.pie(percentages, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)

    ax1.axis('equal')

    return 'pie', mpld3.fig_to_html(fig1)


def scatter_chart(csv, x_label, y_label):
    print("Generating scatter markers")
    scatter_chart = Scatter(csv, x=x_label, y=y_label, title=x_label + " vs " + y_label,
                            xlabel=x_label, ylabel=y_label)
    return 'scatter', convert_chart(scatter_chart)


def scatter_chart_grouped(csv, x_label, y_label, grouped_by):
    print("Generating scatter markers")
    scatter_chart = Scatter(csv, x=x_label, y=y_label, color=grouped_by,
                            title=x_label + " vs " + y_label + " (shaded by " + grouped_by + ")",
                            xlabel=x_label, ylabel=y_label)
    return 'scatter_group', convert_chart(scatter_chart)


def line_graph(csv, x_label, y_label):
    print("Generating line graph")
    # if label_header is not None:
    #     p = figure(plot_width=400, plot_height=400, label=label_header)
    #     p.line(x, y, line_width=2)
    #     q.put(p)
    # else:
    #     p = figure(plot_width=400, plot_height=400)
    #     p.line(x, y, line_width=2)
    #     q.put(('line',p))

    line = Line(csv, y=y_label, x=x_label)
    return 'line', convert_chart(line)


def multiple_lines(csv, x_label, y_label, grouped_by):
    print("Generating multiple lines graph")
    line = Line(csv, y=y_label, x=x_label, color=grouped_by)
    return 'line_multi', convert_chart(line)
