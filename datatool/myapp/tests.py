from queue import Queue

from bokeh.plotting import Figure
from django.test import TestCase
from datatool.myapp.analyzetools.tools import Tools
import pandas as pd
from bokeh.charts import Chart


class ToolsTestCase(TestCase):

    # Instantiate the Tools class and give it a CSV file we can work on
    def setUp(self):
        self.tools = Tools()
        csv = pd.read_csv('media/documents/testdocs/FL_insurance_sample.csv')
        self.tools.set_csv(csv)

    # Test of maximum_value function to check if we receive the correct data
    def test_maximum_value(self):
        queue = Queue()
        # Get the two objects with each their max (eq_site_limit and point_longitude)
        # and get the data for policyID, county, and statecode
        self.tools.maximum_value(queue, ['eq_site_limit', 'point_longitude'], ['policyID', 'county', 'statecode'])

        maxi = queue.get()
        # Check if the policyID retrieved in the objects are correct
        print(maxi[1])
        self.assertEqual(maxi[1][0].info_headers['policyID'], 340585)
        self.assertEqual(maxi[1][1].info_headers['policyID'], 154795)

    def test_bar_chart(self):
        queue = Queue()
        self.tools.bar_chart(queue, "county")
        self.assertIsInstance(queue.get()[1], Chart)

    def test_histogram(self):
        queue = Queue()
        self.tools.histogram(queue, value_header="point_granularity")
        self.tools.histogram(queue, value_header="point_granularity", label_header="county")
        hist1 = queue.get()
        hist2 = queue.get()
        self.assertIsInstance(hist1[1], Chart)
        self.assertIsInstance(hist2[1], Chart)
        self.assertEqual(hist1[0], "hist")
        self.assertEqual(hist1[0], "hist")

    def test_occurences(self):
        queue = Queue()
        self.tools.occurences(queue, ("county", "statecode"))
        occ = queue.get()
        self.assertEqual(occ[1][1].info_headers['FL'], 36634)
        self.assertEqual(occ[1][0].info_headers['DUVAL COUNTY'], 1894)