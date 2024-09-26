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
from datetime import datetime
from pathlib import Path

from utils.config_loader import load_config
from SPASE_JSONLD_converter import convert_spase_to_jsonld

def setup_logging(log_level):
    """Sets up logging configuration."""
    log_format = '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format=log_format,
        handlers=[
            logging.FileHandler("crawler.log"),
            logging.StreamHandler()
        ]
    )

def create_output_directories(base_output_dir, data_types):
    """Creates output directories for each data type."""
    output_dirs = {}
    for data_type in data_types:
        dir_path = base_output_dir / data_type
        dir_path.mkdir(parents=True, exist_ok=True)
        output_dirs[data_type] = dir_path
        logging.debug(f"Ensured output directory exists: {dir_path}")
    return output_dirs

def add_to_sitemap(sitemap_file, file_path, base_url):
    """Adds a new entry to the sitemap.xml file."""
    try:
        if not Path(sitemap_file).exists() or Path(sitemap_file).stat().st_size == 0:
            # Create a new sitemap if it doesn't exist or is empty
            root = ET.Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
            tree = ET.ElementTree(root)
            logging.debug("Created new sitemap root.")
        else:
            tree = ET.parse(sitemap_file)
            root = tree.getroot()
            logging.debug(f"Parsed existing sitemap: {sitemap_file}")
    except ET.ParseError as e:
        logging.error(f"ParseError while parsing sitemap: {e}. Creating a new sitemap.")
        root = ET.Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
        tree = ET.ElementTree(root)

    # Convert file_path to use forward slashes and remove any leading slashes
    relative_path = Path(file_path).as_posix().lstrip('/')

    # Construct the full URL
    full_url = urljoin(base_url, relative_path)
    logging.debug(f"Constructed full URL: {full_url}")

    # Create new url element
    url_element = ET.SubElement(root, 'url')
    loc = ET.SubElement(url_element, 'loc')
    loc.text = full_url

    # Add lastmod element
    lastmod = ET.SubElement(url_element, 'lastmod')
    lastmod.text = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    # Write the updated XML to the sitemap file
    tree.write(sitemap_file, encoding='utf-8', xml_declaration=True)
    logging.info(f"Added URL to sitemap: {full_url}")

def determine_data_type(file_path, data_types):
    """
    Determines the data type of a JSON file based on its directory path.
    Assumes that data type directories are named after the data types.
    """
    path_parts = Path(file_path).parts
    for part in path_parts:
        if part in data_types:
            return part
    return None  # Unknown data type

def should_skip_file(file_path, skip_patterns):
    """
    Determines whether a file should be skipped based on patterns in its path.

    Parameters:
        file_path (Path): The path to the file.
        skip_patterns (list): A list of string patterns to match against the file's path.

    Returns:
        bool: True if the file should be skipped, False otherwise.
    """
    file_path_str = str(file_path).lower()
    for pattern in skip_patterns:
        if pattern.lower() in file_path_str:
            return True
    return False

def process_json_file(json_file_path, output_dirs, sitemap_file, base_url, data_type, generated_files_counter):
    """Processes a single JSON file and converts it to JSON-LD."""
    logging.info(f"Processing file: {json_file_path}")
    try:
        jsonld = convert_spase_to_jsonld(
                input_file=json_file_path,
                base_url=base_url,
                output_file_path=output_dirs[data_type] / f"{Path(json_file_path).stem}.jsonld",
                data_type=data_type
            )
        
        # Write to output file
        output_file = output_dirs[data_type] / f"{Path(json_file_path).stem}.jsonld"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(jsonld, f, indent=2)
        logging.info(f"JSON-LD file created at: {output_file}")

        # Increment the generated files counter
        generated_files_counter[data_type] += 1

        # Add to sitemap
        add_to_sitemap(sitemap_file, output_file, base_url)

    except Exception as e:
        logging.exception(f"Failed to process JSON file: {json_file_path}")
        # Here you can add the file to a list of skipped files or perform other error handling as needed.

def crawl_hpde_directory(root_dir, output_dir, sitemap_file, base_url, data_types, skip_patterns=None):
    """
    Crawls the HPDE directory recursively and processes JSON files based on their data types,
    excluding files that match skip patterns.

    Parameters:
        root_dir (Path): The root directory to start crawling.
        output_dir (Path): The base output directory for JSON-LD files.
        sitemap_file (Path): The path to the sitemap.xml file.
        base_url (str): The base URL for constructing full URLs.
        data_types (list): List of data types to process.
        skip_patterns (list, optional): List of string patterns to exclude.
    """
    output_dirs = create_output_directories(output_dir, data_types)
    root_path = Path(root_dir)

    logging.info(f"Starting recursive crawl in: {root_dir}")

    # Initialize counters
    processed_files_counter = {data_type: 0 for data_type in data_types}
    generated_files_counter = {data_type: 0 for data_type in data_types}
    total_files = 0
    number_skipped_files = 0

    for json_file in root_path.rglob('*.json'):
        total_files += 1

        # Check if the file should be skipped
        if skip_patterns and should_skip_file(json_file, skip_patterns):
            logging.warning(f"Skipping file due to skip pattern: {json_file}")
            number_skipped_files+= 1
            continue

        data_type = determine_data_type(json_file, data_types)
        if data_type:
            logging.debug(f"Determined data type '{data_type}' for file: {json_file}")
            process_json_file(json_file, output_dirs, sitemap_file, base_url, data_type, generated_files_counter)
            processed_files_counter[data_type] += 1
        else:
            logging.warning(f"Could not determine data type for file: {json_file}. Skipping.")

    # Print the counters
    logging.info("Crawl completed.")
    logging.info(f"Processed files count: {processed_files_counter}")
    logging.info(f"Generated JSON-LD files count: {generated_files_counter}")
    logging.info(f"Total files processed: {total_files}")
    logging.info(f"Total files skipped: {number_skipped_files}")

def main():
    """Main function to initiate the crawling process."""
    config = load_config()
    setup_logging(config.get('log_level', 'DEBUG'))

    root_dir = Path(config.get('root_dir', '../hpde.io'))
    output_dir = Path(config.get('output_dir', './ODIS_JSONLD'))
    sitemap_file = Path(config.get('sitemap_file', './sitemap.xml'))
    base_url = config.get('base_url', "https://raw.githubusercontent.com/lechatpito/NASA-ODIS-Examples/main/")
    datatypes = config.get('datatypes', ['DisplayData', 'NumericalData'])
    skip_patterns = config.get('skip_patterns', ['deprecated'])

    logging.info("Starting HPDE crawler")
    crawl_hpde_directory(root_dir, output_dir, sitemap_file, base_url, datatypes, skip_patterns)
    logging.info("HPDE crawler finished")

if __name__ == "__main__":
    main()







