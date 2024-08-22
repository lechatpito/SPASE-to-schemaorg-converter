import unittest
import json
import os
import logging
from SPASE_JSONLD_converter import convert_spase_to_jsonld

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class TestSPASEJSONLDConverter(unittest.TestCase):

    def setUp(self):
        # Create a mock SPASE JSON input
        self.mock_input = {
            "Spase": {
                "DisplayData": {
                    "ResourceID": "spase://NASA/NumericalData/ACE/SWEPAM/PT1H",
                    "ResourceHeader": {
                        "ResourceName": "ACE SWEPAM Level 2 Data",
                        "Contact": {
                            "PersonID": "spase://SMWG/Person/John.Doe"
                        },
                        "ReleaseDate": "2023-01-01T00:00:00Z"
                    },
                    "TemporalDescription": {
                        "TimeSpan": {
                            "StartDate": "1997-08-27",
                            "RelativeStopDate": "PRESENT"
                        }
                    },
                    "ObservedRegion": ["Earth.Magnetosphere", "Sun"],
                    "MeasurementType": "Plasma",
                    "Keyword": ["Solar Wind", "Magnetosphere"]
                }
            }
        }

        # Write the mock input to a temporary file
        self.input_file = 'input.json'
        with open(self.input_file, 'w') as f:
            json.dump(self.mock_input, f)

        # Log the current working directory and file path for debugging
        logging.debug(f"Current working directory: {os.getcwd()}")
        logging.debug(f"Input file path: {os.path.abspath(self.input_file)}")

        # Define the output directory
        self.output_directory = './output'

    def tearDown(self):
        # Remove the temporary input file
        if os.path.exists(self.input_file):
           os.remove(self.input_file)
        if os.path.exists(self.output_file):
           os.remove(self.output_file)
           

    def test_convert_spase_to_jsonld(self):
        # Call the conversion function and get the output file path
        output_file = convert_spase_to_jsonld(self.input_file, self.output_directory)

        # Ensure the output file was returned
        self.assertIsNotNone(output_file, "Output file not returned")
        self.assertTrue(os.path.isfile(output_file), "Output file does not exist")

        # Read the output file
        with open(output_file, 'r') as f:
            jsonld_output = json.load(f)

        # Validate the JSON-LD structure
        self.assertIn('@context', jsonld_output)
        self.assertIn('@type', jsonld_output)
        self.assertEqual(jsonld_output['@type'], 'Dataset')
        self.assertIn('identifier', jsonld_output)
        self.assertIn('name', jsonld_output)
        self.assertIn('url', jsonld_output)
        self.assertIn('publisher', jsonld_output)
        self.assertIn('sdDatePublished', jsonld_output)
        self.assertIn('sdPublisher', jsonld_output)

        # Additional checks can be added here to validate the content

if __name__ == '__main__':
    unittest.main()