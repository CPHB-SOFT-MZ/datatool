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

