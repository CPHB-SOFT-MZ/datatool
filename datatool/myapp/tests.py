from django.test import TestCase
from datatool.myapp.analyzetools.tools import Tools
import pandas as pd


class ToolsTestCase(TestCase):

    # Instantiate the Tools class and give it a CSV file we can work on
    def setUp(self):
        self.tools = Tools()
        csv = pd.read_csv('media/documents/testdocs/FL_insurance_sample.csv')
        self.tools.set_csv(csv)

    # Test of maximum_value function to check if we receive the correct data
    def test_maximum_value(self):
        # Get the two objects with each their max (eq_site_limit and point_longitude)
        # and get the data for policyID, county, and statecode
        l = self.tools.maximum_value(['eq_site_limit', 'point_longitude'], ['policyID', 'county', 'statecode'])

        # Check if the policyID retrieved in the objects are correct
        self.assertEqual(l[0].policyID, 340585)
        self.assertEqual(l[1].policyID, 154795)