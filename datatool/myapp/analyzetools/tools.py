import pandas as pd
import numpy as np

class Tools:
    def maximum_value(self, csv, header):
        return np.amax(np.array(csv[header]))

