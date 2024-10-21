import csv
import yaml
import logging
import json
from datetime import datetime
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD
from urllib.parse import urljoin

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(config_file):
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def load_mapping(file_path, base_uri):
    logger.info(f"Loading mapping from {file_path}")
    with open(file_path, 'r') as f:
        mapping = yaml.safe_load(f)
    
    # Replace $(base_uri) with the actual base_uri
    mapping['prefixes']['base'] = mapping['prefixes']['base'].replace('$(base_uri)', base_uri)
    return mapping

def create_uri(template, row, prefixes):
    for key, value in row.items():
        template = template.replace(f'$({key[1:-1]})', value)
    
    # Handle prefixed URIs
    prefix, local = template.split(':', 1)
    base = prefixes.get(prefix, prefix + ':')
    return URIRef(urljoin(base, local))

def convert_to_rdf(config):
    logger.info(f"Starting conversion process with base URI: {config['base_uri']}")
    mapping = load_mapping(config['mapping_file'], config['base_uri'])
    g = Graph()

    # Define namespaces
    prefixes = {}
    for prefix, uri in mapping['prefixes'].items():
        prefixes[prefix] = uri
        g.bind(prefix, Namespace(uri))
    logger.info("Namespaces defined")

    schema = Namespace('https://schema.org/')

    with open(config['input_file'], 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        row_count = 0
        for row in reader:
            row_count += 1
            if row_count % 1000 == 0:
                logger.info(f"Processed {row_count} rows")
            
            # Create storm observation
            obs_uri = create_uri(mapping['mappings']['storm_observation']['s'], row, prefixes)
            g.add((obs_uri, RDF.type, schema.WeatherObservation))
            
            # Add properties
            for prop in mapping['mappings']['storm_observation']['po']:
                if isinstance(prop, list):
                    if len(prop) == 2:
                        p, o = prop
                        if p == 'a':
                            continue
                        p = schema[p.split(':')[1]]
                        o = o.replace('$(year)', row['<year>']).replace('$(month)', row['<month>']).replace('$(day)', row['<day>']).replace('$(hour)', row['<hour>']).replace('$(min>', row['<min>'])
                        g.add((obs_uri, p, Literal(o)))
                    elif len(prop) == 3:
                        p, o, datatype = prop
                        p = schema[p.split(':')[1]]
                        o = o.replace('$(year)', row['<year>']).replace('$(month>', row['<month>']).replace('$(day)', row['<day>']).replace('$(hour)', row['<hour>']).replace('$(min>', row['<min>'])
                        if '$(mlt)' in o:
                            o = row['<mlt>']
                        elif '$(glat)' in o:
                            o = row['<glat>']
                        elif '$(glon)' in o:
                            o = row['<glon>']
                        g.add((obs_uri, p, Literal(o, datatype=XSD[datatype.split(':')[1]])))
                    else:
                        logger.warning(f"Unexpected number of elements in property list: {prop}")
                elif isinstance(prop, dict):
                    p = schema[prop['p'].split(':')[1]]
                    if prop['o'][0]['mapping'] == 'mlt_technique':
                        mlt_uri = create_uri(mapping['mappings']['mlt_technique']['s'], row, prefixes)
                        g.add((obs_uri, p, mlt_uri))
                        g.add((mlt_uri, RDF.type, schema.PropertyValue))
                        g.add((mlt_uri, schema.name, Literal("Magnetic Local Time")))
                        g.add((mlt_uri, schema.value, Literal(row['<mlt>'])))
                        g.add((mlt_uri, schema.unitCode, Literal("h")))
                    elif prop['o'][0]['mapping'] == 'geo_coordinates':
                        geo_uri = create_uri(mapping['mappings']['geo_coordinates']['s'], row, prefixes)
                        g.add((obs_uri, p, geo_uri))
                        g.add((geo_uri, RDF.type, schema.GeoCoordinates))
                        g.add((geo_uri, schema.latitude, Literal(row['<glat>'], datatype=XSD.float)))
                        g.add((geo_uri, schema.longitude, Literal(row['<glon>'], datatype=XSD.float)))
                    elif prop['o'][0]['mapping'] == 'magnetic_latitude':
                        mlat_uri = create_uri(mapping['mappings']['magnetic_latitude']['s'], row, prefixes)
                        g.add((obs_uri, p, mlat_uri))
                        g.add((mlat_uri, RDF.type, schema.PropertyValue))
                        g.add((mlat_uri, schema.name, Literal("Magnetic Latitude")))
                        g.add((mlat_uri, schema.value, Literal(row['<mlat>'], datatype=XSD.float)))
                        g.add((mlat_uri, schema.unitCode, Literal("DEG")))

    logger.info(f"Processed a total of {row_count} rows")

    # Serialize the graph to JSON-LD
    logger.info(f"Serializing graph to JSON-LD: {config['output_file']}")
    jsonld_data = g.serialize(format='json-ld', indent=2)
    
    # Parse the JSON-LD data and modify the context
    jsonld_obj = json.loads(jsonld_data)
    context = {
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "schema": "https://schema.org/",
        "base": config['base_uri']
    }

    # Function to shorten URIs in the JSON-LD object
    def shorten_uris(obj):
        if isinstance(obj, dict):
            new_obj = {}
            for k, v in obj.items():
                if k == "@id" and v.startswith(config['base_uri']):
                    new_obj[k] = "base:" + v[len(config['base_uri']):]
                elif k.startswith('https://schema.org/'):
                    new_obj['schema:' + k[len('https://schema.org/'):]] = shorten_uris(v)
                else:
                    new_obj[k] = shorten_uris(v)
            return new_obj
        elif isinstance(obj, list):
            return [shorten_uris(item) for item in obj]
        elif isinstance(obj, str):
            if obj.startswith('https://schema.org/'):
                return 'schema:' + obj[len('https://schema.org/'):]
        return obj

    # Apply URI shortening to the JSON-LD object
    jsonld_obj = shorten_uris(jsonld_obj)

    # Access the nested dataset_metadata
    dataset_config = config.get('dataset_metadata', {})

    # Define dataset_metadata using values from config
    dataset_metadata = {
        "@id": dataset_config.get('dataset_id', 'https://example.com/dataset/substorms'),
        "@url": dataset_config.get('dataset_url', 'https://example.com/dataset/substorms'),
        "@type": "schema:Dataset",
        "schema:name": dataset_config.get('name', 'Substorms Dataset'),
        "schema:description": dataset_config.get('description', 'Dataset containing substorm observations'),
        "schema:abstract": dataset_config.get('abstract', ''),
        "schema:license": dataset_config.get('license', ''),
        "schema:audience": [{"@type": "schema:Audience", "schema:audienceType": audience_type} for audience_type in dataset_config.get('audience_types', [])],
        "schema:publisher": {
            "@type": "schema:Organization",
            "schema:name": dataset_config.get('publisher', {}).get('name', ''),
            "schema:url": dataset_config.get('publisher', {}).get('url', '')
        },
        "schema:includedInDataCatalog": {
            "@type": "schema:DataCatalog",
            "schema:name": dataset_config.get('data_catalog', {}).get('name', ''),
            "schema:url": dataset_config.get('data_catalog', {}).get('url', '')
        }
    }

    # Add the context and metadata to the JSON-LD object
    jsonld_obj = {'@context': context, **dataset_metadata, 'schema:hasPart': jsonld_obj}
    
    # Write the JSON-LD to a file
    with open(config['output_file'], 'w') as f:
        json.dump(jsonld_obj, f, indent=2)
    
    logger.info("Conversion process completed")

if __name__ == "__main__":
    config_file = "experiments/substorms_config.yaml"
    config = load_config(config_file)
    
    logger.info("Starting the RDF conversion script")
    convert_to_rdf(config)
    logger.info("RDF conversion script completed")
