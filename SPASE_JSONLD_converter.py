import json
import logging
from urllib.parse import urljoin
from pathlib import Path
from mapping_engine import MappingEngine  # Import the mapping engine

class SPASEConverter:
    """
    Base class for converting SPASE JSON to JSON-LD format.
    """

    def __init__(self, input_file, base_url, output_file_path, data_type, mapping_spec_path):
        self.input_file = Path(input_file)
        self.base_url = base_url
        self.output_file_path = Path(output_file_path)
        self.data_type = data_type
        self.mapping_engine = MappingEngine(mapping_spec_path)
        self.jsonld = {}

    def load_spase_data(self):
        """Loads SPASE JSON data from the input file."""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                self.spase_data = json.load(f)
            logging.debug(f"Loaded SPASE data from {self.input_file}")
        except Exception as e:
            logging.error(f"Failed to read input file {self.input_file}: {e}")
            raise

    def convert(self):
        """Performs the full conversion process."""
        self.load_spase_data()
        self.extracted_data = self.spase_data.get('Spase', {}).get(self.data_type, {})
        if isinstance(self.extracted_data, list):
            self.extracted_data = self.extracted_data[0]
        logging.debug(f"Extracted data section for {self.data_type}")

        self.jsonld["@id"] = urljoin(self.base_url, self.clean_path())
        self.jsonld["url"] = self.jsonld["@id"]

        mapped_jsonld = self.mapping_engine.apply_mappings(self.data_type, self.spase_data, self.base_url)
        self.jsonld.update(mapped_jsonld)

        return self.jsonld

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

    def save_jsonld(self):
        """Saves the JSON-LD data to the output file."""
        self.mapping_engine.save_jsonld(self.jsonld, self.output_file_path)

class DisplayDataConverter(SPASEConverter):
    """
    Converter for DisplayData SPASE JSON to JSON-LD.
    """

    def __init__(self, input_file, base_url, output_file_path):
        super().__init__(input_file, base_url, output_file_path, data_type='DisplayData')


class NumericalDataConverter(SPASEConverter):
    """
    Converter for NumericalData SPASE JSON to JSON-LD.
    """

    def __init__(self, input_file, base_url, output_file_path):
        super().__init__(input_file, base_url, output_file_path, data_type='NumericalData')

def convert_spase_to_jsonld(input_file, base_url, output_file_path, data_type, mapping_spec_path):
    """
    Factory function to convert SPASE JSON to JSON-LD based on data type.

    Parameters:
        input_file (str): Path to the input SPASE JSON file.
        base_url (str): Base URL for constructing @id and URLs.
        output_file_path (str): Path to save the output JSON-LD file.
        data_type (str): Type of data (e.g., 'DisplayData', 'NumericalData').
        mapping_spec_path (str): Path to the mapping spec file.
    Returns:
        dict: Converted JSON-LD data.
    """
    if data_type == 'DisplayData':
        converter = DisplayDataConverter(input_file, base_url, output_file_path, mapping_spec_path)
    elif data_type == 'NumericalData':
        converter = NumericalDataConverter(input_file, base_url, output_file_path, mapping_spec_path)
    else:
        raise ValueError(f"Unsupported data type: {data_type}")

    jsonld = converter.convert()
    converter.save_jsonld()
    return jsonld