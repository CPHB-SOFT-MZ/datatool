from django.test import TestCase
from datatool.datatool.analyzetools.tools import *
import pandas as pd


class ToolsTestCase(TestCase):
    # Instantiate the Tools class and give it a CSV file we can work on
    def setUp(self):
        self.csv = pd.read_csv('media/documents/testdocs/FL_insurance_sample.csv')

    # Test of maximum_value function to check if we receive the correct data
    def test_maximum_value(self):
        # Get the two objects with each their max (eq_site_limit and point_longitude)
        # and get the data for policyID, county, and statecode
        maxi = maximum_value(self.csv, ['eq_site_limit', 'point_longitude'], ['policyID', 'county', 'statecode'])

        # Check if the policyID retrieved in the objects are correct
        self.assertEqual(maxi[1][0].info_headers['policyID'], 340585)
        self.assertEqual(maxi[1][1].info_headers['policyID'], 154795)

    def test_bar_chart(self):
        bar = bar_chart(self.csv, "county")
        self.assertIsInstance(bar[1]['script'], str)

    def test_bar_chart_sum(self):
        bar = bar_chart_sum(self.csv, "tiv_2012", "county")
        self.assertIsInstance(bar[1]['script'], str)

    def test_histogram(self):
        hist = histogram(csv=self.csv, value_header="point_granularity", label_header="county")

        self.assertIsInstance(hist[1]['script'], str)
        self.assertEqual(hist[0], "hist")

    def test_occurences(self):
        occ = occurrences(self.csv, ("county", "statecode"))
        self.assertEqual(occ[1][1].value_headers['FL'], 36634)
        self.assertEqual(occ[1][0].value_headers['DUVAL COUNTY'], 1894)

    def test_sums(self):
        ss = sums(self.csv, ["tiv_2011"])
        self.assertEqual(ss[1][0].value_headers, {'tiv_2011': 79601102761.830002})

    def test_average_values(self):
        ss = average_value(self.csv, ['tiv_2011'])
        self.assertEqual(ss[1][0].value_headers, {'tiv_2011': 2172875.000322924})

    def test_average_values_for(self):
        ss = average_value_for(self.csv, ['tiv_2011', 'tiv_2012'], "county")
        self.assertEqual(ss[1][0].value_headers, {'tiv_2011': 847914.22266187065, 'tiv_2012': 1021623.7854573485})

    def test_median_values(self):
        med = median_value_for(self.csv, ['tiv_2011'], "county")
        self.assertEqual(med[1][0].value_headers, {'tiv_2011': 60795.0})
