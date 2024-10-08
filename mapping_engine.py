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
    if regions:
        if isinstance(regions, str):
            return [{"@type": "Place", "name": regions}]
        elif isinstance(regions, list):
            return [{"@type": "Place", "name": region} for region in regions]
        # elif isinstance(regions, dict):
        #     return [{"@type": "Place", "name": regions.get('ObservedRegion', '')}]
        else:
            logging.warning(f"Unexpected type for regions: {type(regions)} -- {regions}")
            return []
    else:
        return []

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
            "name": name,
            "description": description
        })
        if encoding_format:
            distribution[0]["encodingFormat"] = encoding_format
    return distribution

def map_parameters(parameters):
    variable_measured = []
    if not isinstance(parameters, list):
        parameters = [parameters]
    for parameter in parameters:
        if isinstance(parameter, dict):
            variable = {
                    "@type": "PropertyValue"
            }
            
            name = parameter.get('Name')
            if name:
                variable["name"] = name

            description = parameter.get('Description')
            if description:
                variable["description"] = description

            unit_text = parameter.get('Units')
            if unit_text:
                variable["unitText"] = unit_text

            min_value = parameter.get('ValidMin')
            if min_value:
                variable["minValue"] = min_value

            max_value = parameter.get('ValidMax')
            if max_value:
                variable["maxValue"] = max_value

            default_value = parameter.get('FillValue')
            if default_value:
                variable["defaultValue"] = default_value
                
            cadence = parameter.get('Cadence')
            if cadence:
                variable["cadence"] = cadence
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
            source_value = self.get_nested_value(data_section, source_field)    

             # Skip if source_value is empty
            if not source_value:
                logging.info(f"Skipping mapping for {source_field} as no data is present.")
                continue

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
