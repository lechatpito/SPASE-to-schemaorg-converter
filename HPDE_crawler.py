# This module crawls the HPDE file directory
# For each directory, it looks for DisplayData or NumericalData subdirectories
# It recursively crawls all subdirectories to find JSON files
# Converts found JSON files to JSON-LD using the SPASE_JSONLD_converter module
# Stores the JSON-LD files in the ODIS_JSONLD directory
# Updates the sitemap.xml file with new entries
# Logs processing information and errors

import os
import json
import xml.etree.ElementTree as ET
import logging
from urllib.parse import urljoin

from utils.config_loader import load_config
from SPASE_JSONLD_converter import convert_spase_to_jsonld, convert_numerical_to_jsonld

def setup_logging(log_level):
    """Sets up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("crawler.log"),
            logging.StreamHandler()
        ]
    )

def crawl_hpde_directory(root_dir, output_dir, sitemap_file, base_url, datatypes):
    """Crawls the HPDE directory to find and process JSON files."""
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Remove 'Deprecated' from dirnames if it exists
        if 'Deprecated' in dirnames:
            dirnames.remove('Deprecated')
            logging.info(f"Removed 'Deprecated' directory from scanning: {dirpath}")

        for data_dir in datatypes:
            if data_dir in dirnames:
                data_directory = os.path.join(dirpath, data_dir)
                logging.info(f"Processing data directory: {data_directory}")
                process_data_directory(data_directory, output_dir, sitemap_file, base_url, data_dir)

def process_data_directory(directory, output_dir, sitemap_file, base_url, data_type):
    """Processes a specific data directory to find and convert JSON files."""
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.json'):
                json_file_path = os.path.join(dirpath, filename)
                try:
                    process_json_file(json_file_path, output_dir, sitemap_file, base_url, data_type)
                except Exception as e:
                    logging.error(f"Error processing file {json_file_path}: {e}")
                    add_to_skipped_files(output_dir, json_file_path, str(e))

def process_json_file(json_file_path, output_dir, sitemap_file, base_url, data_type):
    """Processes a single JSON file and converts it to JSON-LD."""
    logging.info(f"Processing file: {json_file_path}")

    # Generate the new file name
    relative_path = os.path.relpath(json_file_path, start=os.path.dirname(output_dir))
    path_parts = relative_path.split(os.sep)

    # Remove specified directories from the path parts
    path_parts = [part for part in path_parts if part not in ['..', 'hpde.io', 'DisplayData', 'NumericalData']]
    new_file_name = '_'.join(path_parts)
    new_file_name = os.path.splitext(new_file_name)[0] + '.jsonld'

    # Create the full output path
    output_file_path = os.path.join(output_dir, new_file_name)

    # Convert the SPASE JSON to JSON-LD
    if data_type == 'DisplayData':
        jsonld_content = convert_spase_to_jsonld(json_file_path, base_url, output_file_path)
    elif data_type == 'NumericalData':
        jsonld_content = convert_numerical_to_jsonld(json_file_path, base_url, output_file_path)
    else:
        logging.warning(f"Unsupported data type '{data_type}' for file {json_file_path}. Skipping.")
        return

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    # Write the JSON-LD content to the new file
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(jsonld_content, f, indent=2)
    logging.info(f"Created JSON-LD file: {output_file_path}")

    # Add the new file to the sitemap
    add_to_sitemap(sitemap_file, output_file_path, base_url)

def add_to_sitemap(sitemap_file, file_path, base_url):
    """Adds a new entry to the sitemap.xml file."""
    if not os.path.exists(sitemap_file):
        # Create a new sitemap if it doesn't exist
        root = ET.Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
        tree = ET.ElementTree(root)
    else:
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

    # Add lastmod element
    lastmod = ET.SubElement(url, 'lastmod')
    lastmod.text = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    # Write the updated XML to the sitemap file
    tree.write(sitemap_file, encoding='utf-8', xml_declaration=True)
    logging.info(f"Added URL to sitemap: {full_url}")

def add_to_skipped_files(output_dir, file_path, reason):
    """Logs skipped files with reasons."""
    skipped_files_path = os.path.join(output_dir, 'skipped_files.txt')
    with open(skipped_files_path, 'a', encoding='utf-8') as f:
        f.write(f"{file_path}: {reason}\n")
    logging.info(f"Logged skipped file: {file_path} Reason: {reason}")

def main():
    """Main function to initiate the crawling process."""
    config = load_config()
    setup_logging(config.get('log_level', 'INFO'))

    root_dir = config.get('root_dir', '../hpde.io')
    output_dir = config.get('output_dir', './ODIS_JSONLD')
    sitemap_file = config.get('sitemap_file', './sitemap.xml')
    base_url = config.get('base_url', "https://raw.githubusercontent.com/lechatpito/NASA-ODIS-Examples/main/")
    datatypes = config.get('datatypes', ['DisplayData', 'NumericalData'])

    logging.info("Starting HPDE crawler")
    crawl_hpde_directory(root_dir, output_dir, sitemap_file, base_url, datatypes)
    logging.info("HPDE crawler finished")

if __name__ == "__main__":
    main()







