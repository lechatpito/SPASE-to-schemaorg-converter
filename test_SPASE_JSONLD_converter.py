import unittest
import json
import os
from pathlib import Path
from mapping_engine import MappingEngine
import yaml
import logging

class TestMappingEngine(unittest.TestCase):

    def setUp(self):
        mapping_spec_file = 'mapping/mapping_spec.yaml'
        
        # Initialize the MappingEngine
        self.mapping_engine = MappingEngine(mapping_spec_file)

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

        # Define a sample SPASE JSON input for NumericalData
        self.spase_json_numerical = {
            "Spase": {
                "xmlns": "http://www.spase-group.org/data/schema",
                "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "xsi:schemaLocation": "http://www.spase-group.org/data/schema http://www.spase-group.org/data/schema/spase-2_3_0.xsd",
                "Version": "2.3.0",
                "NumericalData": {
                    "ResourceID": "spase://GBO/NumericalData/Almeria/Magnetometer/PT1H/ASCII_FORMAT",
                    "ResourceHeader": {
                        "ResourceName": "Almeria Magnetometer 1-hr Data in ASCII Flat Table Format",
                        "ReleaseDate": "2019-05-05T12:34:56Z",
                        "Description": "Almeria Magnetometer data, 1-hr time resoluion, in ASCII format. Magnetic Field Vector Element List: DHZ. Note that the list of magnetic field elements that appear in the data set may change over the course of time. For instance, many stations have shifted from DHZ to the XYZ representation of the magnetic field. The time history listed below summarizes changes in element content. A description of the WDC Data Exchange Format for CADENCE magnetic field data is included at the end of this data product description.",
                        "Acknowledgement": "Please acknowledge: Almeria Observatory Director for providing the data observations, and the British Geological Survey, World Data Center for Geomagnetism, Edinburgh for providing access to the data.",
                        "Contact": [
                            {
                                "PersonID": "spase://SMWG/Person/WDC/Director.Almeria.Observatory",
                                "Role": [
                                    "GeneralContact",
                                    "DataProducer"
                                ]
                            },
                            {
                                "PersonID": "spase://SMWG/Person/Lee.Frost.Bargatze",
                                "Role": [
                                    "MetadataContact",
                                    "TechnicalContact"
                                ]
                            }
                        ],
                        "InformationURL": {
                            "Name": "The Geomagnetic Data Master Catalog at the WDC for Geomagnetism, Edinburgh",
                            "URL": "http://www.wdc.bgs.ac.uk/catalog/intro.html",
                            "Description": "Web site for access to magnetometer data hosted by the World Data Center for Geomagnetism, Edinburgh"
                        },
                        "Association": {
                            "AssociationID": "spase://GBO/NumericalData/Almeria/Magnetometer/PT1H/WDC_FORMAT",
                            "AssociationType": "DerivedFrom"
                        },
                        "PriorID": [
                            "spase://VMO/NumericalData/Almeria/Magnetometer/PT1H/ASCII",
                            "spase://VMO/NumericalData/Almeria/Magnetometer/PT1H/ASCII_FORMAT"
                        ]
                    },
                    "AccessInformation": {
                        "RepositoryID": "spase://SMWG/Repository/UCLA/VMO",
                        "Availability": "Online",
                        "AccessRights": "Open",
                        "AccessURL": {
                            "Name": "The UCLA VMO Data Repository",
                            "URL": "http://vmo.igpp.ucla.edu/data1/WDC/MAGNETOGRAM/Almeria/PT1H/TXT/",
                            "Description": "The Virtual Magnetospheric Observatory (VMO) Data Repository hosted by the Institute of Geophysics and Planetary Physics (IGPP) at the University of California, Los Angeles (UCLA)."
                        },
                        "Format": "Text",
                        "Encoding": "GZIP",
                        "DataExtent": {
                            "Quantity": "825696",
                            "Units": "bytes",
                            "Per": "P1Y"
                        },
                        "Acknowledgement": "Please thank the British Geological Survey, World Data Center, Edinburgh for use of data from the WDC Geomagnetic Data Master Catalog. The WDC to ASCII translation was performed at UCLA and the derived ASCII formatted data are available via the UCLA VMO data repository."
                    },
                    "ProcessingLevel": "Calibrated",
                    "InstrumentID": "spase://SMWG/Instrument/Ground/Almeria/Magnetometer",
                    "MeasurementType": "MagneticField",
                    "TemporalDescription": {
                        "TimeSpan": {
                            "StartDate": "1957-07-01T00:00:00.000",
                            "StopDate": "1966-03-31T23:00:00.000",
                            "Note": "Some data gaps may be present. If a gap is present at the beginning or end of the file, the time span start and stop dates could be inaccurate as they are assigned assuming an absence of such gaps."
                        },
                        "Cadence": "PT1H"
                    },
                    "ObservedRegion": "Earth.Surface",
                    "Keyword": [
                        "ground station",
                        "magnetometer",
                        "magnetic field",
                        "magnetogram",
                        "Almeria",
                        "WDC Station Code: ALM",
                        "1-hour",
                        "ASCII Flat File",
                        "ASCII Flat Table"
                    ],
                    "Parameter": [
                        {
                            "Name": "Universal Time",
                            "ParameterKey": "Time",
                            "Description": "Time is expressed using a five column format with the following order: year, month, day, hour, and minute, each stored in interger format. The time columns are the first five columns (1,2,3,4,5) in the flat file.",
                            "Cadence": "PT1H",
                            "Structure": {
                                "Size": "5",
                                "Description": "Universal Time expressed using a 5-column year, month, day, hour, minute representation",
                                "Element": [
                                    {
                                        "Name": "Year",
                                        "Index": "1",
                                        "ParameterKey": "Column_1"
                                    },
                                    {
                                        "Name": "Month",
                                        "Index": "2",
                                        "ParameterKey": "Column_2"
                                    },
                                    {
                                        "Name": "Day",
                                        "Index": "3",
                                        "ParameterKey": "Column_3"
                                    },
                                    {
                                        "Name": "Hour",
                                        "Index": "4",
                                        "ParameterKey": "Column_4"
                                    },
                                    {
                                        "Name": "Minute",
                                        "Index": "5",
                                        "ParameterKey": "Column_5"
                                    }
                                ]
                            },
                            "Support": {
                                "SupportQuantity": "Temporal"
                            }
                        },
                        {
                            "Name": "Magnetic Field DHZ",
                            "Description": "Almeria Magnetic Field in DHZ Coordinates",
                            "Cadence": "PT1H",
                            "CoordinateSystem": {
                                "CoordinateRepresentation": "Cylindrical",
                                "CoordinateSystemName": "CGM"
                            },
                            "Structure": {
                                "Size": "3",
                                "Description": "Almeria Magnetic Field Data in DHZ Coordinates. The DHZ data columns are numbers (6,8,11) in the flat file.",
                                "Element": [
                                    {
                                        "Name": "D",
                                        "Qualifier": "DirectionAngle.AzimuthAngle",
                                        "Index": "1",
                                        "ParameterKey": "Column_6",
                                        "Units": "Degree",
                                        "UnitsConversion": "2*pi > Radian",
                                        "ValidMin": "-180.0",
                                        "ValidMax": "180.0",
                                        "FillValue": "-99999.999"
                                    },
                                    {
                                        "Name": "H",
                                        "Qualifier": "Projection.IJ",
                                        "Index": "2",
                                        "ParameterKey": "Column_8",
                                        "Units": "nT",
                                        "UnitsConversion": "10^9 >T",
                                        "ValidMin": "-70000",
                                        "ValidMax": "70000",
                                        "FillValue": "-99999.999"
                                    },
                                    {
                                        "Name": "Z",
                                        "Qualifier": "Component.K",
                                        "Index": "3",
                                        "ParameterKey": "Column_11",
                                        "Units": "nT",
                                        "UnitsConversion": "10^9 >T",
                                        "ValidMin": "-70000",
                                        "ValidMax": "70000",
                                        "FillValue": "-99999.999"
                                    }
                                ]
                            },
                            "Field": {
                                "Qualifier": "Vector",
                                "FieldQuantity": "Magnetic"
                            }
                        },
                        {
                            "Name": "Almeria Magnetic Field XYZ",
                            "Description": "Almeria Magnetic Field in XYZ coordinates",
                            "Cadence": "PT1H",
                            "CoordinateSystem": {
                                "CoordinateRepresentation": "Cartesian",
                                "CoordinateSystemName": "CGM"
                            },
                            "Structure": {
                                "Size": "3",
                                "Description": "Almeria Magnetic Field Data in XYZ Coordinates. The XYZ data columns are numbers (9,10,11) in the flat file.",
                                "Element": [
                                    {
                                        "Name": "X",
                                        "Qualifier": "Component.I",
                                        "Index": "1",
                                        "ParameterKey": "Column_9",
                                        "Units": "nT",
                                        "UnitsConversion": "10^9 >T",
                                        "ValidMin": "-70000",
                                        "ValidMax": "70000",
                                        "FillValue": "-99999.999"
                                    },
                                    {
                                        "Name": "Y",
                                        "Qualifier": "Component.J",
                                        "Index": "2",
                                        "ParameterKey": "Column_10",
                                        "Units": "nT",
                                        "UnitsConversion": "10^9 >T",
                                        "ValidMin": "-70000",
                                        "ValidMax": "70000",
                                        "FillValue": "-99999.999"
                                    },
                                    {
                                        "Name": "Z",
                                        "Qualifier": "Component.K",
                                        "Index": "3",
                                        "ParameterKey": "Column_11",
                                        "Units": "nT",
                                        "UnitsConversion": "10^9 >T",
                                        "ValidMin": "-70000",
                                        "ValidMax": "70000",
                                        "FillValue": "-99999.999"
                                    }
                                ]
                            },
                            "Field": {
                                "Qualifier": "Vector",
                                "FieldQuantity": "Magnetic"
                            }
                        },
                        {
                            "Name": "Magnetic Field Inclination",
                            "ParameterKey": "Column_7",
                            "Description": "Almeria Magnetic Field Vector Inclination",
                            "Cadence": "PT1H",
                            "Units": "Degree",
                            "UnitsConversion": "2*pi > Radian",
                            "ValidMin": "-180.0",
                            "ValidMax": "180.0",
                            "FillValue": "-99999.999",
                            "Field": {
                                "Qualifier": "DirectionAngle.ElevationAngle",
                                "FieldQuantity": "Magnetic"
                            }
                        },
                        {
                            "Name": "Magnetic Field Magnitude",
                            "ParameterKey": "Column_12",
                            "Description": "Almeria Magnetic Field Vector Magnitude",
                            "Cadence": "PT1H",
                            "Units": "nT",
                            "UnitsConversion": "10^9 >T",
                            "ValidMin": "0",
                            "ValidMax": "70000",
                            "FillValue": "-99999.999",
                            "Field": {
                                "Qualifier": "Magnitude",
                                "FieldQuantity": "Magnetic"
                            }
                        }
                    ]
                }
            }
        }

    def tearDown(self):
        pass

    def test_display_data_mapping(self):
        """Test the mapping of DisplayData SPASE JSON to JSON-LD."""
        base_url = 'https://hpde.io/'
        data_type = 'DisplayData'

        logging.info("Testing DisplayData mapping")

        # Pass only the 'DisplayData' part of the JSON
        display_data = self.spase_json_display.get('Spase', {}).get('DisplayData', {})
        
        jsonld = self.mapping_engine.apply_mappings(data_type, display_data, base_url)

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

    def test_numerical_data_mapping(self):
        """Test the mapping of NumericalData SPASE JSON to JSON-LD."""
        base_url = 'https://hpde.io/'
        data_type = 'NumericalData'

        logging.info("Testing NumericalData mapping")
        
        # Pass only the 'NumericalData' part of the JSON
        numerical_data = self.spase_json_numerical.get('Spase', {}).get('NumericalData', {})

        jsonld = self.mapping_engine.apply_mappings(data_type, numerical_data, base_url)
        
        # Print a pretty version of the jsonld content
        # print("JSON-LD Content:")
        # print(json.dumps(jsonld, indent=2))

        # Assertions for @id and url
        expected_id = 'https://hpde.io/GBO/NumericalData/Almeria/Magnetometer/PT1H/ASCII_FORMAT'
        self.assertEqual(jsonld["@id"], expected_id)
        self.assertEqual(jsonld["url"], expected_id)

        # Assertions for name
        self.assertIn("name", jsonld)
        self.assertEqual(jsonld["name"], "Almeria Magnetometer 1-hr Data in ASCII Flat Table Format")

        # Assertions for sdDatePublished
        self.assertIn("sdDatePublished", jsonld)
        self.assertEqual(jsonld["sdDatePublished"], "2019-05-05")

        # Assertions for description
        self.assertIn("description", jsonld)
        self.assertIn("abstract", jsonld)
        self.assertEqual(jsonld["description"], "Almeria Magnetometer data, 1-hr time resoluion, in ASCII format. Magnetic Field Vector Element List: DHZ. Note that the list of magnetic field elements that appear in the data set may change over the course of time. For instance, many stations have shifted from DHZ to the XYZ representation of the magnetic field. The time history listed below summarizes changes in element content. A description of the WDC Data Exchange Format for CADENCE magnetic field data is included at the end of this data product description.")
        self.assertEqual(jsonld["abstract"], "Almeria Magnetometer data, 1-hr time resoluion, in ASCII format. Magnetic Field Vector Element List: DHZ. Note that the list of magnetic field elements that appear in the data set may change over the course of time. For instance, many stations have shifted from DHZ to the XYZ representation of the magnetic field. The time history listed below summarizes changes in element content. A description of the WDC Data Exchange Format for CADENCE magnetic field data is included at the end of this data product description.")

        # Assertions for spatialCoverage
        self.assertIn("spatialCoverage", jsonld)
        expected_spatial = [{"@type": "Place", "name": "Earth.Surface"}]
        self.assertEqual(jsonld["spatialCoverage"], expected_spatial)

        # Assertions for keywords
        self.assertIn("keywords", jsonld)
        self.assertEqual(jsonld["keywords"], ["ground station", "magnetometer", "magnetic field", "magnetogram", "Almeria", "WDC Station Code: ALM", "1-hour", "ASCII Flat File", "ASCII Flat Table"])

        # Assertions for distribution
        self.assertIn("distribution", jsonld)
        expected_distribution = [{
            "@type": "DataDownload",
            "contentUrl": "http://vmo.igpp.ucla.edu/data1/WDC/MAGNETOGRAM/Almeria/PT1H/TXT/",
            "name": "The UCLA VMO Data Repository",
            "description": "The Virtual Magnetospheric Observatory (VMO) Data Repository hosted by the Institute of Geophysics and Planetary Physics (IGPP) at the University of California, Los Angeles (UCLA)."
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

        # Assertions for Parameter fields such as Universal Time and Magnetic Field
        self.assertIn("variableMeasured", jsonld)
        self.assertEqual(len(jsonld["variableMeasured"]), 5)

        # Universal Time
        universal_time = jsonld["variableMeasured"][0]
        self.assertEqual(universal_time["@type"], "PropertyValue")
        self.assertEqual(universal_time["name"], "Universal Time")
        self.assertEqual(universal_time["description"], "Time is expressed using a five column format with the following order: year, month, day, hour, and minute, each stored in interger format. The time columns are the first five columns (1,2,3,4,5) in the flat file.")
        self.assertEqual(universal_time["cadence"], "PT1H")
        
        # Magnetic Field DHZ
        magnetic_field_dhz = jsonld["variableMeasured"][1]
        self.assertEqual(magnetic_field_dhz["@type"], "PropertyValue")
        self.assertEqual(magnetic_field_dhz["name"], "Magnetic Field DHZ")
        self.assertEqual(magnetic_field_dhz["description"], "Almeria Magnetic Field in DHZ Coordinates")
        self.assertEqual(magnetic_field_dhz["cadence"], "PT1H")
        
        # Almeria Magnetic Field XYZ
        magnetic_field_xyz = jsonld["variableMeasured"][2]
        self.assertEqual(magnetic_field_xyz["@type"], "PropertyValue")
        self.assertEqual(magnetic_field_xyz["name"], "Almeria Magnetic Field XYZ")
        self.assertEqual(magnetic_field_xyz["description"], "Almeria Magnetic Field in XYZ coordinates")
        self.assertEqual(magnetic_field_xyz["cadence"], "PT1H")
        
        # Magnetic Field Inclination
        magnetic_field_inclination = jsonld["variableMeasured"][3]
        self.assertEqual(magnetic_field_inclination["@type"], "PropertyValue")
        self.assertEqual(magnetic_field_inclination["name"], "Magnetic Field Inclination")
        self.assertEqual(magnetic_field_inclination["description"], "Almeria Magnetic Field Vector Inclination")
        self.assertEqual(magnetic_field_inclination["cadence"], "PT1H")
        
        # Magnetic Field Magnitude
        magnetic_field_magnitude = jsonld["variableMeasured"][4]
        self.assertEqual(magnetic_field_magnitude["@type"], "PropertyValue")
        self.assertEqual(magnetic_field_magnitude["name"], "Magnetic Field Magnitude")
        self.assertEqual(magnetic_field_magnitude["description"], "Almeria Magnetic Field Vector Magnitude")
        self.assertEqual(magnetic_field_magnitude["cadence"], "PT1H")
        
if __name__ == '__main__':
    unittest.main()