import unittest
import json
import os
from pathlib import Path
from mapping_engine import MappingEngine
import yaml
class TestMappingEngine(unittest.TestCase):

    def setUp(self):
        # Define a sample mapping specification
        self.mapping_spec = {
            "DisplayData": {
                "mappings": {                                        
                    "ResourceID": {
                        "targets": ["@id", "url"],
                        "transform": "to_url"
                    },
                    "ResourceHeader.ResourceName": {
                        "target": "name",
                        "transform": None
                    },
                    "ResourceHeader.ReleaseDate": {
                        "target": "sdDatePublished",
                        "transform": "extract_date"
                    },
                    "ResourceHeader.Description": {
                        "targets": ["description", "abstract"],
                        "transform": None
                    },
                    "ObservedRegion": {
                        "target": "spatialCoverage",
                        "transform": "map_to_place"
                    },
                    "Keyword": {
                        "target": "keywords",
                        "transform": None
                    },
                    "AccessInformation.AccessURL": {
                        "target": "distribution",
                        "transform": "map_distribution"
                    }
                }
            }
        }
        # Write the mapping spec to a temporary YAML file
        self.mapping_spec_path = 'temp_mapping_spec.yaml'
        with open(self.mapping_spec_path, 'w') as f:
            yaml.dump(self.mapping_spec, f)

        # Initialize the MappingEngine
        self.mapping_engine = MappingEngine(self.mapping_spec_path)

        # Define a sample SPASE JSON input for DisplayData
        self.spase_json_display = {
            "Spase": {
                "DisplayData": {
                    "ResourceID": "spase://NASA/DisplayData/ACE/SWEPAM/PT1H",
                    "ResourceHeader": {
                        "ResourceName": "ACE SWEPAM Level 2 Data",
                        "Contact": {
                            "PersonID": "spase://SMWG/Person/John.Doe"
                        },
                        "ReleaseDate": "2023-01-01T00:00:00Z",
                        "Description": "Description of DisplayData"
                    },
                    "ObservedRegion": ["Earth.Magnetosphere", "Sun"],
                    "Keyword": ["Solar Wind", "Magnetosphere"],
                    "AccessInformation": {
                        "AccessURL": {
                            "URL": "https://example.com/data/display",
                            "Name": "Display Data Download",
                            "Description": "Download link for Display Data",
                            "Format": "JSON"
                        }
                    }
                }
            }
        }

    def tearDown(self):
        # Remove the temporary mapping spec file
        if Path(self.mapping_spec_path).exists():
            os.remove(self.mapping_spec_path)

    def test_display_data_mapping(self):
        """Test the mapping of DisplayData SPASE JSON to JSON-LD."""
        base_url = 'https://hpde.io/'
        data_type = 'DisplayData'

        # Pass only the 'DisplayData' part of the JSON
        display_data = self.spase_json_display.get('Spase', {}).get('DisplayData', {})
       
        jsonld = self.mapping_engine.apply_mappings(data_type, display_data, base_url)
        # Print a pretty version of the jsonld content
        import json
        print("JSON-LD Content:")
        print(json.dumps(jsonld, indent=2))

        # Assertions for @id and url
                
        expected_id = 'https://hpde.io/NASA/DisplayData/ACE/SWEPAM/PT1H'
        self.assertEqual(jsonld["@id"], expected_id)
        self.assertEqual(jsonld["url"], expected_id)

        # Assertions for name
        self.assertIn("name", jsonld)
        self.assertEqual(jsonld["name"], "ACE SWEPAM Level 2 Data")

        # Assertions for sdDatePublished
        self.assertIn("sdDatePublished", jsonld)
        self.assertEqual(jsonld["sdDatePublished"], "2023-01-01")

        # Assertions for description and abstract
        self.assertIn("description", jsonld)
        self.assertIn("abstract", jsonld)
        self.assertEqual(jsonld["description"], "Description of DisplayData")
        self.assertEqual(jsonld["abstract"], "Description of DisplayData")

        # Assertions for spatialCoverage
        self.assertIn("spatialCoverage", jsonld)
        expected_spatial = [{"@type": "Place", "name": "Earth.Magnetosphere"}, {"@type": "Place", "name": "Sun"}]
        self.assertEqual(jsonld["spatialCoverage"], expected_spatial)

        # Assertions for keywords
        self.assertIn("keywords", jsonld)
        self.assertEqual(jsonld["keywords"], ["Solar Wind", "Magnetosphere"])

        # Assertions for distribution
        self.assertIn("distribution", jsonld)
        expected_distribution = [{
            "@type": "DataDownload",
            "contentUrl": "https://example.com/data/display",
            "encodingFormat": "JSON",
            "name": "Display Data Download",
            "description": "Download link for Display Data"
        }]
        self.assertEqual(jsonld["distribution"], expected_distribution)

        # Assertions for hardcoded fields
        self.assertIn("license", jsonld)
        self.assertEqual(jsonld["license"], "https://cdla.io/permissive-1-0/")

        self.assertIn("audience", jsonld)
        self.assertEqual(jsonld["audience"]["@type"], "Audience")
        self.assertListEqual(
            jsonld["audience"]["audienceType"],
            ["Space Physicist", "Space Community", "Data Scientists", "Machine Learning Users"]
        )

        self.assertIn("sdPublisher", jsonld)
        self.assertEqual(jsonld["sdPublisher"]["@type"], "Organization")
        self.assertEqual(jsonld["sdPublisher"]["name"], "hpde.io")

        self.assertIn("includedInDataCatalog", jsonld)
        self.assertEqual(jsonld["includedInDataCatalog"]["@type"], "DataCatalog")
        self.assertEqual(jsonld["includedInDataCatalog"]["name"], "HPDE.io / SPASE")
        self.assertEqual(jsonld["includedInDataCatalog"]["url"], "https://hpde.io/")

if __name__ == '__main__':
    unittest.main()