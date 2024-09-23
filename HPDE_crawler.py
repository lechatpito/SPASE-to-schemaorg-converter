# This module crawls the HPDE file directory
# For each directory, it looks if there is a DisplayData subdirectory
# If there is one, it recursively crawls all subdirectories of DisplayData until it gets a JSON file
# It then parses the JSON file and identifies if there is one or more datasets represented, ie there is only one SPASE.AccessInformation element
# In this case it calls the SPASE_JSONLD_converter module to convert the JSON file to ODIS schema.org JSON-LD
# It then stores the JSON-LD file in the ODIS_JSONLD directory
# It adds the file path in the sitemap.xml file
# If there are more than one access information element, it creates a JSON-LD file for each access information element. However in this case the converter module needs to be rewritten so we'll start only with files with one access information element

import os
import json
import xml.etree.ElementTree as ET
from SPASE_JSONLD_converter import convert_spase_to_jsonld, convert_numerical_to_jsonld
from datetime import datetime
from urllib.parse import urljoin

def crawl_hpde_directory(root_dir, output_dir, sitemap_file, base_url, datatypes):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Remove 'Deprecated' from dirnames if it exists
        if 'Deprecated' in dirnames:
            dirnames.remove('Deprecated')
        
        for data_dir in datatypes:
            if data_dir in dirnames:
                data_directory = os.path.join(dirpath, data_dir)
                process_data_directory(data_directory, output_dir, sitemap_file, base_url, data_dir)

def process_data_directory(directory, output_dir, sitemap_file, base_url, data_type):
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.json'):
                json_file_path = os.path.join(dirpath, filename)
                try:
                    process_json_file(json_file_path, output_dir, sitemap_file, base_url, data_type)
                except Exception as e:
                    print(f"Error processing file {json_file_path}: {e}")

def process_json_file(json_file_path, output_dir, sitemap_file, base_url, data_type):
    print(f"Processing file: {json_file_path}")
    
    try:
        # Generate the new file name
        relative_path = os.path.relpath(json_file_path, start=os.path.dirname(output_dir))
        path_parts = relative_path.split(os.sep)
        
        # Remove 'DisplayData' or 'NumericalData' from the path parts if it exists
        path_parts = [part for part in path_parts if part not in ['..', 'hpde.io', data_type]]
        # Create the new file name
        new_file_name = '_'.join(path_parts)
        new_file_name = os.path.splitext(new_file_name)[0] + '.jsonld'
        
        # Create the full output path
        output_file_path = os.path.join(output_dir, new_file_name)
        
        # Convert the SPASE JSON to JSON-LD
        if data_type == 'DisplayData':
            jsonld_content = convert_spase_to_jsonld(json_file_path, base_url, output_file_path)
        elif data_type == 'NumericalData':
            jsonld_content = convert_numerical_to_jsonld(json_file_path, base_url, output_file_path)
        
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        
        # Write the JSON-LD content to the new file
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(jsonld_content, f, indent=2)
        
        # Add the new file to the sitemap
        add_to_sitemap(sitemap_file, output_file_path, base_url)
        
        print(f"Created JSON-LD file: {output_file_path}")
    
    except UnicodeDecodeError:
        print(f"Error: Unable to decode {json_file_path} using UTF-8 encoding. Skipping this file.")
        add_to_skipped_files(output_dir, json_file_path, "Unable to decode using UTF-8 encoding")
    except json.JSONDecodeError:
        print(f"Error: {json_file_path} is not a valid JSON file. Skipping this file.")
        add_to_skipped_files(output_dir, json_file_path, "Not a valid JSON file")

def add_to_skipped_files(output_dir, file_path, reason):
    skipped_files_path = os.path.join(output_dir, 'skipped_files.txt')
    with open(skipped_files_path, 'a', encoding='utf-8') as f:
        f.write(f"{file_path}: {reason}\n")

def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# def extract_access_info(data):
#     spase = data.get('Spase', [])
#     if isinstance(spase, list):
#         spase = spase[0] if spase else {}
#     display_data = spase.get('DisplayData', {})
#     if isinstance(display_data, list):
#         display_data = display_data[0] if display_data else {}
#    return display_data.get('AccessInformation', {})

# def is_single_access_info(access_info):
#     return isinstance(access_info, dict) and 'AccessURL' in access_info

# def is_multiple_access_info(access_info):
#     return isinstance(access_info, list) or (isinstance(access_info, dict) and isinstance(access_info.get('AccessURL', []), list))

def process_single_access_info(json_file_path, output_dir, sitemap_file, base_url, data_type):
    # Generate the new file name
    relative_path = os.path.relpath(json_file_path, start=os.path.dirname(output_dir))
    path_parts = relative_path.split(os.sep)
    
    # Remove 'DisplayData' or 'NumericalData' from the path parts if it exists
    path_parts = [part for part in path_parts if part not in ['..', 'hpde.io', data_type]]
    # Create the new file name
    new_file_name = '_'.join(path_parts)
    new_file_name = os.path.splitext(new_file_name)[0] + '.jsonld'
    
    # Create the full output path
    output_file_path = os.path.join(output_dir, new_file_name)
    
    # Convert the SPASE JSON to JSON-LD
    if data_type == 'DisplayData':
        jsonld_content = convert_spase_to_jsonld(json_file_path, base_url, output_file_path)
    elif data_type == 'NumericalData':
        jsonld_content = convert_numerical_to_jsonld(json_file_path, base_url, output_file_path)
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    
    # Write the JSON-LD content to the new file
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(jsonld_content, f, indent=2)
    
    # Add the new file to the sitemap
    add_to_sitemap(sitemap_file, output_file_path, base_url)
    
    print(f"Created JSON-LD file: {output_file_path}")

def add_to_sitemap(sitemap_file, file_path, base_url):
    tree = ET.parse(sitemap_file)
    root = tree.getroot()
    
    # Convert file_path to use forward slashes and remove any leading slashes
    relative_path = file_path.replace(os.sep, '/').lstrip('/')

    # Construct the full URL
    full_url = urljoin(base_url, relative_path)

    # Create new url element
    url = ET.SubElement(root, 'url')
    loc = ET.SubElement(url, 'loc')
    loc.text = full_url

    # Add lastmod element (optional)
    lastmod = ET.SubElement(url, 'lastmod')
    lastmod.text = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+00:00')

    # Write the updated XML to the sitemap file
    tree.write(sitemap_file, encoding='utf-8', xml_declaration=True)
    
def main():
    root_dir = '../hpde.io'
    base_output_dir = './ODIS_JSONLD'
    sitemap_file = './sitemap.xml'
    base_url = "https://raw.githubusercontent.com/lechatpito/NASA-ODIS-Examples/main/"
    datatypes = ['NumericalData'] #['DisplayData', 
                 
    # Create subfolders for each datatype
    for datatype in datatypes:
        output_dir = os.path.join(base_output_dir, datatype)
        os.makedirs(output_dir, exist_ok=True)
        crawl_hpde_directory(root_dir, output_dir, sitemap_file, base_url, [datatype])    

if __name__ == "__main__":
    main()







