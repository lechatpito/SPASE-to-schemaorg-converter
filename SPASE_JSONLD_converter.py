import json
from datetime import datetime, timedelta
import os

def convert_spase_to_jsonld(input_file):
    # Read the input JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        spase_data = json.load(f)

    # Extract the DisplayData section
    display_data = spase_data['Spase']['DisplayData']
    if isinstance(display_data, list):
        display_data = display_data[0]

    # Create the base JSON-LD structure
    jsonld = {
        "@context": {
            "@vocab": "https://schema.org/"
        },
        "@type": "Dataset"
    }

    # Map fields from SPASE to JSON-LD
    jsonld["@id"] = f"https://hpde.io/{display_data['ResourceID'].split('://')[-1]}"
    jsonld["name"] = display_data['ResourceHeader']['ResourceName']
    jsonld["url"] = f"{jsonld['@id']}.html"
    
    # Publisher information
    if 'Contact' in display_data['ResourceHeader'] and 'PersonID' in display_data['ResourceHeader']['Contact']:
        jsonld["publisher"] = {
            "@type": "Person",
            "identifier": display_data['ResourceHeader']['Contact']['PersonID'],
            "url": f"http://hpde.io/{display_data['ResourceHeader']['Contact']['PersonID'].split('://')[-1]}"
        }

    if 'ReleaseDate' in display_data['ResourceHeader']:
        jsonld["sdDatePublished"] = display_data['ResourceHeader']['ReleaseDate'][:10]

    jsonld["sdPublisher"] = {
        "@type": "Organization",
        "name": "hpde.io"
    }

    # Distribution information
    if 'AccessInformation' in display_data and 'AccessURL' in display_data['AccessInformation']:
        access_url = display_data['AccessInformation']['AccessURL']
        if isinstance(access_url, list):
            access_url = access_url[0]
        jsonld["distribution"] = {
            "@type": "DataDownload",
            "contentUrl": access_url['URL'],
            "encodingFormat": display_data['AccessInformation'].get('Format', '')
        }

    jsonld["includedInDataCatalog"] = {
        "@type": "DataCatalog",
        "name": "HPDE.io / SPASE",
        "url": "https://hpde.io/"
    }

    if 'ResourceID' in display_data:
        jsonld["identifier"] = display_data['ResourceID']

    resource_header = display_data.get('ResourceHeader', {})
    if 'ResourceName' in resource_header:
        jsonld["creditText"] = f"{resource_header['ResourceName']}."
    if 'Description' in resource_header:
        jsonld["description"] = resource_header['Description']
        jsonld["abstract"] = resource_header['Description']

    # Temporal coverage
    time_span = display_data.get('TemporalDescription', {}).get('TimeSpan', {})
    start_date = time_span.get('StartDate')
    relative_stop_date = time_span.get('RelativeStopDate')
    if start_date or relative_stop_date:
        jsonld["temporalCoverage"] = f"Start date: {start_date}. Relative stop date: {relative_stop_date}"

    if 'MeasurementType' in display_data:
        jsonld["variableMeasured"] = display_data['MeasurementType']

    # Spatial coverage
    observed_regions = display_data.get('ObservedRegion', [])
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

    if 'Keyword' in display_data:
        jsonld["keywords"] = display_data['Keyword']
    jsonld["license"] = "https://cdla.io/permissive-1-0/"
    jsonld["audience"] = {
        "@type": "Audience",
        "audienceType": ["Space Physicist", "Space Community", "Data Scientists", "Machine Learning Users"]
    }

    return jsonld
def main():
    # Example usage
    input_file = 'source.spase.json'
    output_directory = './output'
    output_file = convert_spase_to_jsonld(input_file, output_directory)
    print(f"Output written to {output_file}")

if __name__ == "__main__":
    main()
