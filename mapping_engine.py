import json
import logging
from pathlib import Path
from urllib.parse import urljoin
import yaml
from datetime import datetime

# Define transformation functions
def to_url(resource_id, base_url):
    # Ensure resource_id is a string
    if isinstance(resource_id, dict):
        # Extract the appropriate string value from the dictionary
        resource_id = resource_id.get("URL")  # Adjust this key as necessary

    # Check if resource_id is None or not a string
    if resource_id is None or not isinstance(resource_id, str):
        logging.warning(f"Invalid resource_id: {resource_id}")
        return ''  # or handle it as needed

    identifier = resource_id.split('://')[-1]
    return f"{base_url}{identifier}"

def extract_date(datetime_str):
    return datetime_str.split('T')[0] if 'T' in datetime_str else datetime_str

def map_to_place(regions):
    return [{"@type": "Place", "name": region} for region in regions]

def map_distribution(access_urls, data_section, base_url):
    distribution = []
    if isinstance(access_urls, dict):
        access_urls = [access_urls]
    for access_url in access_urls:
        content_url = parse_access_url(access_url)
        encoding_format = access_url.get('Format', '') #if isinstance(data_section.get('AccessInformation', {}), dict) else ''
        name = access_url.get('Name', '') if isinstance(access_url, dict) else ''
        description = access_url.get('Description', '') if isinstance(access_url, dict) else ''
        distribution.append({
            "@type": "DataDownload",
            "contentUrl": content_url,
            "encodingFormat": encoding_format,
            "name": name,
            "description": description
        })
    return distribution

def map_parameters(parameters):
    variable_measured = []
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
                variable["structure"] = handle_structure(structure)
            variable_measured.append(variable)
        else:
            logging.warning(f"Skipping non-dict parameter: {parameter}")
    return variable_measured

def handle_structure(structure):
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

def parse_access_url(access_url):
    if isinstance(access_url, str):
        return access_url
    elif isinstance(access_url, dict):
        return access_url.get('URL', '')
    elif isinstance(access_url, list) and access_url:
        return parse_access_url(access_url[0]) if isinstance(access_url[0], dict) else ''
    else:
        logging.warning(f"Unexpected access_url format: {access_url}")
        return ''

# Mapping of transformation names to functions
TRANSFORM_FUNCTIONS = {
    "to_url": to_url,
    "extract_date": extract_date,
    "map_to_place": map_to_place,
    "map_distribution": map_distribution,
    "map_parameters": map_parameters,
    # Add more transformations as needed
}

class MappingEngine:
    def __init__(self, mapping_spec_path):
        self.mapping_spec = self.load_mapping_spec(mapping_spec_path)

    def load_mapping_spec(self, path):
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def apply_mappings(self, data_type, spase_json, base_url):
        # url = to_url(spase_json.get('Spase', {}).get('DisplayData', {}).get('ResourceID', ''), base_url)
        jsonld = {
            "@context": {
                "@vocab": "https://schema.org/"
            },
            "@type": "Dataset",
            # Ensure @id is set correctly
            # "@id": url
        }
        mappings = self.mapping_spec.get(data_type, {}).get('mappings', {})
        data_section = spase_json.get('Spase', {}).get(data_type, {})
        for source_field, config in mappings.items():            
            # Handle nested source fields
            source_value = self.get_nested_value(spase_json, source_field)
            if 'transform' in config and config['transform']:
                transform_func = TRANSFORM_FUNCTIONS.get(config['transform'])
                if transform_func:
                    if config['transform'] == "to_url":
                        transformed_value = transform_func(source_value, base_url)
                    elif config['transform'] == "map_distribution":
                        transformed_value = transform_func(source_value, data_section, base_url)
                    else:
                        transformed_value = transform_func(source_value)
                else:
                    logging.warning(f"No transformation function found for {config['transform']}")
                    transformed_value = source_value
            else:
                transformed_value = source_value

            # Apply to single target or multiple targets
            if 'target' in config:
                jsonld[config['target']] = transformed_value
            elif 'targets' in config:
                for target_field in config['targets']:
                    jsonld[target_field] = transformed_value

        # Additional hardcoded fields
        jsonld["license"] = "https://cdla.io/permissive-1-0/"
        jsonld["audience"] = {
            "@type": "Audience",
            "audienceType": [
                "Space Physicist",
                "Space Community",
                "Data Scientists",
                "Machine Learning Users"
            ]
        }
        jsonld["sdPublisher"] = {
            "@type": "Organization",
            "name": "hpde.io"
        }
        jsonld["includedInDataCatalog"] = {
            "@type": "DataCatalog",
            "name": "HPDE.io / SPASE",
            "url": "https://hpde.io/"
        }

        return jsonld

    def get_nested_value(self, data, field_path):
        keys = field_path.split('.')
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key, {})
            else:
                return {}
        return data

    def save_jsonld(self, jsonld, output_path):
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(jsonld, f, indent=2)
            logging.info(f"JSON-LD file created at: {output_path}")
        except Exception as e:
            logging.error(f"Failed to write JSON-LD file {output_path}: {e}")
            raise
