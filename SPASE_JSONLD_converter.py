# This module provides functions to convert SPASE JSON to JSON-LD format based on data type.

import json
import logging
from urllib.parse import urljoin
from pathlib import Path

class SPASEConverter:
    """
    Base class for converting SPASE JSON to JSON-LD format.
    """

    def __init__(self, input_file, base_url, output_file_path, data_type):
        self.input_file = Path(input_file)
        self.base_url = base_url
        self.output_file_path = Path(output_file_path)
        self.data_type = data_type
        self.jsonld = {
            "@context": {
                "@vocab": "https://schema.org/"
            },
            "@type": "Dataset",
        }

    def load_spase_data(self):
        """Loads SPASE JSON data from the input file."""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                self.spase_data = json.load(f)
            logging.debug(f"Loaded SPASE data from {self.input_file}")
        except Exception as e:
            logging.error(f"Failed to read input file {self.input_file}: {e}")
            raise

    def extract_data_section(self):
        """Extracts the relevant data section based on data type."""
        self.data_section = self.spase_data.get('Spase', {}).get(self.data_type, {})
        if isinstance(self.data_section, list):
            self.data_section = self.data_section[0]
        logging.debug(f"Extracted data section for {self.data_type}")

    def clean_path(self):
        """Cleans the output file path to create a relative path for the JSON-LD @id."""
        try:
            relative_path = self.output_file_path.relative_to(self.output_file_path.parents[2])  # Adjust based on directory structure
        except ValueError:
            logging.error(f"Cannot determine relative path for {self.output_file_path}. Check directory structure.")
            relative_path = self.output_file_path.name  # Fallback to filename

        path_parts = relative_path.as_posix().split('/')
        path_parts = [part for part in path_parts if part not in ['..', 'hpde.io']]
        cleaned_path = '/'.join(path_parts)
        logging.debug(f"Cleaned path: {cleaned_path}")
        return cleaned_path

    def extract_access_urls(self):
        """Extracts AccessURL entries from AccessInformation."""
        access_info = self.data_section.get('AccessInformation', {})
        access_urls = []

        if isinstance(access_info, dict):
            access_urls = access_info.get('AccessURL', [])
        elif isinstance(access_info, list):
            for item in access_info:
                if isinstance(item, dict):
                    access_urls.extend(item.get('AccessURL', []))
        else:
            logging.warning(f"Unexpected AccessInformation format: {access_info}")

        # Normalize access_urls to a list
        if isinstance(access_urls, dict):
            access_urls = [access_urls]
        elif isinstance(access_urls, str):
            access_urls = [access_urls]

        logging.debug(f"Extracted access URLs: {access_urls}")
        return access_urls

    def parse_access_url(self, access_url):
        """Parses the access_url based on its type."""
        if isinstance(access_url, str):
            return access_url
        elif isinstance(access_url, dict):
            return access_url.get('URL', '')
        elif isinstance(access_url, list) and access_url:
            return self.parse_access_url(access_url[0]) if isinstance(access_url[0], dict) else ''
        else:
            logging.warning(f"Unexpected access_url format: {access_url}")
            return ''

    def map_publisher_information(self):
        """Maps publisher information from SPASE to JSON-LD."""
        contacts = self.data_section.get('ResourceHeader', {}).get('Contact', [])
        if not isinstance(contacts, list):
            contacts = [contacts]
        person_ids = [contact.get('PersonID', '') for contact in contacts if contact.get('PersonID')]
        if person_ids:
            self.jsonld["publisher"] = []
            for person_id in person_ids:
                identifier = person_id.split('://')[-1]
                self.jsonld["publisher"].append({
                    "@type": "Person",
                    "identifier": person_id,
                    "url": urljoin(self.base_url, identifier)
                })
            logging.debug(f"Mapped publisher information: {self.jsonld['publisher']}")

    def map_release_date(self):
        """Maps release date from SPASE to JSON-LD."""
        release_date = self.data_section.get('ReleaseDate', '')
        if release_date:
            self.jsonld["sdDatePublished"] = release_date[:10]
            logging.debug(f"Mapped release date: {self.jsonld['sdDatePublished']}")

    def map_publisher_organization(self):
        """Maps publisher organization information to JSON-LD."""
        self.jsonld["sdPublisher"] = {
            "@type": "Organization",
            "name": "hpde.io"
        }
        logging.debug("Mapped publisher organization.")

    def map_distribution_information(self):
        """Maps distribution information from SPASE to JSON-LD."""
        access_urls = self.extract_access_urls()
        self.jsonld["distribution"] = []
        for access_url in access_urls:
            distribution = {
                "@type": "DataDownload",
                "contentUrl": self.parse_access_url(access_url),
                "encodingFormat": self.data_section.get('Format', '') if isinstance(self.data_section.get('AccessInformation', {}), dict) else '',
                "name": access_url.get('Name', '') if isinstance(access_url, dict) else '',
                "description": access_url.get('Description', '') if isinstance(access_url, dict) else ''
            }
            self.jsonld["distribution"].append(distribution)
        logging.debug(f"Mapped distribution information: {self.jsonld['distribution']}")

    def map_data_catalog(self):
        """Maps data catalog information to JSON-LD."""
        self.jsonld["includedInDataCatalog"] = {
            "@type": "DataCatalog",
            "name": "HPDE.io / SPASE",
            "url": "https://hpde.io/"
        }
        logging.debug("Mapped data catalog information.")

    def map_additional_fields(self):
        """Maps additional fields like identifier, description, abstract."""
        if 'ResourceID' in self.data_section:
            self.jsonld["identifier"] = self.data_section['ResourceID']
            logging.debug(f"Mapped identifier: {self.jsonld['identifier']}")

        description = self.data_section.get('Description', '')
        self.jsonld["description"] = description
        self.jsonld["abstract"] = description
        logging.debug(f"Mapped description and abstract: {description}")

    def map_observed_regions(self):
        """Maps observed regions to JSON-LD."""
        observed_regions = self.data_section.get('ObservedRegion', [])
        if observed_regions:
            self.jsonld["spatialCoverage"] = [{"@type": "Place", "name": region} for region in observed_regions]
            logging.debug(f"Mapped observed regions: {self.jsonld['spatialCoverage']}")

    def map_keywords(self):
        """Maps keywords to JSON-LD."""
        keywords = self.data_section.get('Keyword', [])
        if keywords:
            self.jsonld["keywords"] = keywords
            logging.debug(f"Mapped keywords: {keywords}")

    def map_license(self):
        """Maps license information to JSON-LD."""
        self.jsonld["license"] = "https://cdla.io/permissive-1-0/"
        logging.debug("Mapped license information.")

    def map_audience(self):
        """Maps audience information to JSON-LD."""
        self.jsonld["audience"] = {
            "@type": "Audience",
            "audienceType": [
                "Space Physicist",
                "Space Community",
                "Data Scientists",
                "Machine Learning Users"
            ]
        }
        logging.debug("Mapped audience information.")

    def save_jsonld(self):
        """Saves the JSON-LD data to the output file."""
        try:
            with open(self.output_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.jsonld, f, indent=2)
            logging.info(f"JSON-LD file created at: {self.output_file_path}")
        except Exception as e:
            logging.error(f"Failed to write JSON-LD file {self.output_file_path}: {e}")
            raise

    def convert(self):
        """Performs the full conversion process."""
        self.load_spase_data()
        self.extract_data_section()
        self.jsonld["@id"] = urljoin(self.base_url, self.clean_path())
        self.jsonld["url"] = self.jsonld["@id"]

        self.map_publisher_information()
        self.map_release_date()
        self.map_publisher_organization()
        self.map_distribution_information()
        self.map_data_catalog()
        self.map_additional_fields()
        self.map_observed_regions()
        self.map_keywords()
        self.map_license()
        self.map_audience()

        return self.jsonld


class DisplayDataConverter(SPASEConverter):
    """
    Converter for DisplayData SPASE JSON to JSON-LD.
    """

    def __init__(self, input_file, base_url, output_file_path):
        super().__init__(input_file, base_url, output_file_path, data_type='DisplayData')

    # Override or extend methods if DisplayData requires specific handling
    # For example, attributes or additional mappings specific to DisplayData
    # Currently, inheritance suffices as both data types share similar mapping.


class NumericalDataConverter(SPASEConverter):
    """
    Converter for NumericalData SPASE JSON to JSON-LD.
    """

    def __init__(self, input_file, base_url, output_file_path):
        super().__init__(input_file, base_url, output_file_path, data_type='NumericalData')

    def map_variable_measured(self):
        """Maps variableMeasured from SPASE to JSON-LD."""
        parameters = self.data_section.get('Parameter', [])
        if parameters:
            self.jsonld["variableMeasured"] = []
            for parameter in parameters:
                if isinstance(parameter, dict):
                    variable = {
                        "@type": "PropertyValue",
                        "name": parameter.get('Name', ''),
                        "description": parameter.get('Description', ''),
                        "unitText": parameter.get('Units', ''),
                        "minValue": parameter.get('ValidMin', ''),
                        "maxValue": parameter.get('ValidMax', ''),
                        "defaultValue": parameter.get('FillValue', '')
                    }
                    # Handle nested structures if present
                    if 'Structure' in parameter:
                        structure = parameter['Structure']
                        variable["structure"] = self.handle_structure(structure)
                    self.jsonld["variableMeasured"].append(variable)
                else:
                    logging.warning(f"Skipping non-dict parameter: {parameter}")
            logging.debug(f"Mapped variableMeasured: {self.jsonld['variableMeasured']}")

    def handle_structure(self, structure):
        """Handles the 'Structure' field in parameters."""
        if isinstance(structure, str):
            return structure
        elif isinstance(structure, dict):
            return {
                "@type": "StructuredValue",
                "size": structure.get('Size', ''),
                "elements": structure.get('Element', [])
            }
        else:
            logging.warning(f"Unexpected structure format: {structure}")
            return ''

    def convert(self):
        """Performs the full conversion process with additional numerical data mappings."""
        super().convert()
        self.map_variable_measured()
        return self.jsonld


def convert_spase_to_jsonld(input_file, base_url, output_file_path, data_type):
    """
    Factory function to convert SPASE JSON to JSON-LD based on data type.

    Parameters:
        input_file (str): Path to the input SPASE JSON file.
        base_url (str): Base URL for constructing @id and URLs.
        output_file_path (str): Path to save the output JSON-LD file.
        data_type (str): Type of data (e.g., 'DisplayData', 'NumericalData').

    Returns:
        dict: Converted JSON-LD data.
    """
    if data_type == 'DisplayData':
        converter = DisplayDataConverter(input_file, base_url, output_file_path)
    elif data_type == 'NumericalData':
        converter = NumericalDataConverter(input_file, base_url, output_file_path)
    else:
        raise ValueError(f"Unsupported data type: {data_type}")

    jsonld = converter.convert()
    converter.save_jsonld()
    return jsonld