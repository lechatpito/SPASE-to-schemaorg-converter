import json
from datetime import datetime, timedelta
import os

def convert_to_jsonld(input_file, base_url, output_file_path, data_type):
    # Read the input JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        spase_data = json.load(f)

    # Extract the data section based on the data_type
    data_section = spase_data['Spase'][data_type]
    if isinstance(data_section, list):
        data_section = data_section[0]

    # Create the base JSON-LD structure
    jsonld = {
        "@context": {
            "@vocab": "https://schema.org/"
        },
        "@type": "Dataset"
    }

    # Map fields from SPASE to JSON-LD
    relative_path = output_file_path.replace(os.sep, '/')
    path_parts = relative_path.split('/')
    # Remove directories to be omitted
    path_parts = [part for part in path_parts if part not in ['..', 'hpde.io', data_type]]
    cleaned_path = '/'.join(path_parts)
    
    jsonld["@id"] = f"{base_url}{cleaned_path}"
    jsonld["name"] = data_section['ResourceHeader']['ResourceName']
    jsonld["url"] = f"{jsonld['@id']}"

    # Publisher information
    if 'Contact' in data_section['ResourceHeader'] and 'PersonID' in data_section['ResourceHeader']['Contact']:
        jsonld["publisher"] = {
            "@type": "Person",
            "identifier": data_section['ResourceHeader']['Contact']['PersonID'],
            "url": f"http://hpde.io/{data_section['ResourceHeader']['Contact']['PersonID'].split('://')[-1]}"
        }

    if 'ReleaseDate' in data_section['ResourceHeader']:
        jsonld["sdDatePublished"] = data_section['ResourceHeader']['ReleaseDate'][:10]

    jsonld["sdPublisher"] = {
        "@type": "Organization",
        "name": "hpde.io"
    }

    # Distribution information
    if 'AccessInformation' in data_section and 'AccessURL' in data_section['AccessInformation']:
        access_urls = data_section['AccessInformation']['AccessURL']
        if not isinstance(access_urls, list):
            access_urls = [access_urls]
        
        jsonld["distribution"] = []
        for access_url in access_urls:
            distribution = {
                "@type": "DataDownload",
                "contentUrl": access_url['URL'],
                "encodingFormat": data_section['AccessInformation'].get('Format', ''),
                "name": access_url.get('Name', ''),
                "description": access_url.get('Description', '')
            }
            jsonld["distribution"].append(distribution)

    jsonld["includedInDataCatalog"] = {
        "@type": "DataCatalog",
        "name": "HPDE.io / SPASE",
        "url": "https://hpde.io/"
    }

    if 'ResourceID' in data_section:
        jsonld["identifier"] = data_section['ResourceID']

    resource_header = data_section.get('ResourceHeader', {})
    if 'ResourceName' in resource_header:
        jsonld["creditText"] = f"{resource_header['ResourceName']}."
    if 'Description' in resource_header:
        jsonld["description"] = resource_header['Description']
        jsonld["abstract"] = resource_header['Description']

    # Temporal coverage
    time_span = data_section.get('TemporalDescription', {}).get('TimeSpan', {})
    start_date = time_span.get('StartDate')
    relative_stop_date = time_span.get('RelativeStopDate')
    if start_date or relative_stop_date:
        jsonld["temporalCoverage"] = f"Start date: {start_date}. Relative stop date: {relative_stop_date}"

    if 'MeasurementType' in data_section:
        jsonld["variableMeasured"] = data_section['MeasurementType']

    # Spatial coverage
    observed_regions = data_section.get('ObservedRegion', [])
    if observed_regions:
        jsonld["spatialCoverage"] = []
        if isinstance(observed_regions, str):
            jsonld["spatialCoverage"] = [{
                "@type": "Place",
                "name": observed_regions
            }]
        else:
            for region in observed_regions:
                jsonld["spatialCoverage"].append({
                    "@type": "Place",
                    "name": f"{region}"
                })

    if 'Keyword' in data_section:
        jsonld["keywords"] = data_section['Keyword']
    jsonld["license"] = "https://cdla.io/permissive-1-0/"
    jsonld["audience"] = {
        "@type": "Audience",
        "audienceType": ["Space Physicist", "Space Community", "Data Scientists", "Machine Learning Users"]
    }

    # Parse parameters (only for NumericalData)
    if data_type == 'NumericalData' and 'Parameter' in data_section:
        jsonld["variableMeasured"] = []
        for parameter in data_section['Parameter']:
            variable = {
                "@type": "PropertyValue",
                "name": parameter['Name'],
                "description": parameter.get('Description', ''),
                "unitText": parameter.get('Units', ''),
                "minValue": parameter.get('ValidMin', ''),
                "maxValue": parameter.get('ValidMax', ''),
                "defaultValue": parameter.get('FillValue', '')
            }

            if 'UnitsConversion' in parameter:
                variable["unitCode"] = parameter['UnitsConversion']

            if 'CoordinateSystem' in parameter:
                variable["measurementTechnique"] = f"{parameter['CoordinateSystem'].get('CoordinateRepresentation', '')} {parameter['CoordinateSystem'].get('CoordinateSystemName', '')}"

            if 'Structure' in parameter:
                variable["valueReference"] = []
                for element in parameter['Structure'].get('Element', []):
                    variable["valueReference"].append({
                        "@type": "PropertyValue",
                        "name": element['Name'],
                        "description": element.get('Qualifier', ''),
                        "position": element.get('Index', ''),
                        "defaultValue": element.get('FillValue', '')
                    })

            if 'Support' in parameter:
                variable["additionalProperty"] = {
                    "@type": "PropertyValue",
                    "name": "Support",
                    "value": parameter['Support'].get('SupportQuantity', '')
                }
                if 'Qualifier' in parameter['Support']:
                    variable["additionalProperty"]["description"] = parameter['Support']['Qualifier']
            
            if 'Field' in parameter:
                if not isinstance(variable.get('additionalProperty'), list):
                    if 'additionalProperty' in variable:
                        variable['additionalProperty'] = [variable['additionalProperty']]
                    else:
                        variable['additionalProperty'] = []
                field_property = {
                    "@type": "PropertyValue",
                    "name": "Field",
                    "value": parameter['Field'].get('FieldQuantity', '')
                }
                if 'Qualifier' in parameter['Field']:
                    field_property["description"] = parameter['Field']['Qualifier']
                variable['additionalProperty'].append(field_property)

            # Add ParameterKey
            if 'ParameterKey' in parameter:
                if not isinstance(variable.get('additionalProperty'), list):
                    variable['additionalProperty'] = [variable['additionalProperty']]
                variable['additionalProperty'].append({
                    "@type": "PropertyValue",
                    "name": "ParameterKey",
                    "value": parameter['ParameterKey']
                })

            # Add Caveats
            if 'Caveats' in parameter:
                if not isinstance(variable.get('additionalProperty'), list):
                    variable['additionalProperty'] = [variable['additionalProperty']]
                variable['additionalProperty'].append({
                    "@type": "PropertyValue",
                    "name": "Caveats",
                    "value": parameter['Caveats']
                })

            # Add Cadence
            if 'Cadence' in parameter:
                if not isinstance(variable.get('additionalProperty'), list):
                    variable['additionalProperty'] = [variable['additionalProperty']]
                variable['additionalProperty'].append({
                    "@type": "PropertyValue",
                    "name": "Cadence",
                    "value": parameter['Cadence']
                })

            # Add RenderingHints
            if 'RenderingHints' in parameter:
                for key, value in parameter['RenderingHints'].items():
                    variable['additionalProperty'].append({
                        "@type": "PropertyValue",
                        "name": key,
                        "value": value
                    })

            jsonld["variableMeasured"].append(variable)

    return jsonld

def convert_spase_to_jsonld(input_file, base_url, output_file_path):
    return convert_to_jsonld(input_file, base_url, output_file_path, 'DisplayData')

def convert_numerical_to_jsonld(input_file, base_url, output_file_path):
    return convert_to_jsonld(input_file, base_url, output_file_path, 'NumericalData')

def main():
    # Example usage
    input_file = 'source.spase.json'
    base_url = 'https://hpde.io/'
    output_directory = './ODIS_JSONLD'
    
    # Generate the output file path
    output_file_name = os.path.splitext(os.path.basename(input_file))[0] + '.jsonld'
    output_file_path = os.path.join(output_directory, output_file_name)
    
    output_file = convert_spase_to_jsonld(input_file, base_url, output_file_path)
    print(f"Output written to {output_file}")

if __name__ == "__main__":
    main()
