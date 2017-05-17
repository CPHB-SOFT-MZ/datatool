import pandas as pd
import numpy as np

class Tools:
    def __init__(self):
        self.csv = ""

    def set_csv(self, csv):
        self.csv = csv

    def maximum_value(self, header):
        return np.amax(np.array(self.csv[header]))

    options = {
        'AMAX' : maximum_value,
    }

