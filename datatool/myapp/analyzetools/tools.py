import pandas as pd
import numpy as np

class Tools:
    def __init__(self):
        self.csv = pd.DataFrame()

    def set_csv(self, csv):
        self.csv = pd.DataFrame(csv)

    # Finds the row with maximum value for each value header and returns the value and all requested info headers
    def maximum_value(self, value_headers, info_headers):
        df_return = []
        for value_header in value_headers:
            df = self.csv[info_headers + [value_header]]
            df_return.append(df.ix[np.argmax(np.array(self.csv[value_header]))])
        return df_return

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
                info, count = np.unique(array, return_counts=true)
                tuple_list.append(zip(info, count))
        return tuple_list
