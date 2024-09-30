# Helio-KNOW ODIS Conversion Tools

## Table of Contents
- [Introduction](#introduction)
- [Why Convert SPASE to ODIS?](#why-convert-spase-to-odis)
- [The Conversion Process](#the-conversion-process)
- [SPASE to ODIS Mapping](#spase-to-odis-mapping)
- [Helio-KNOW: Advancing Heliophysics through Open Science and Knowledge Commons](#helio-know-advancing-heliophysics-through-open-science-and-knowledge-commons)
  - [Project Overview](#project-overview)
  - [Key Objectives](#key-objectives)
  - [The Importance of Open Science in Heliophysics](#the-importance-of-open-science-in-heliophysics)
  - [Benefits for Helio-KNOW](#benefits-for-helio-know)
  - [ODIS Project Integration](#odis-project-integration)
- [How to Use This Repository](#how-to-use-this-repository)
  - [Prerequisites](#prerequisites)
  - [Configuration](#configuration)
  - [Running the Code](#running-the-code)
  - [Adding a New Mapping / Data Type](#adding-a-new-mapping--data-type)
  - [Converting Mappings YAML to Markdown](#converting-mappings-yaml-to-markdown)

## Introduction

This project focuses on converting [SPASE (Space Physics Archive Search and Extract)](https://spase-group.org/) metadata to [ODIS (Ocean Data and Information System)](https://book.odis.org/) compatible JSON-LD format. This conversion is a crucial step in integrating heliophysics data into a broader, interoperable framework that adheres to schema.org vocabulary.

## Why Convert SPASE to ODIS?

1. **Interoperability**: ODIS uses schema.org vocabulary, which enhances interoperability between different data systems and enables easier discovery through major search engines.

2. **Broader Access**: Converting SPASE metadata to ODIS format makes heliophysics data more accessible to researchers outside the immediate field, potentially fostering interdisciplinary collaborations.

3. **Standardization**: By adopting a widely-used standard like schema.org, we ensure that heliophysics data can be easily integrated with other scientific datasets.

4. **Enhanced Discoverability**: The use of schema.org vocabulary improves the discoverability of heliophysics data through commercial search engines and domain-specific portals.

## The Conversion Process

Our conversion process involves two main scripts:

1. `SPASE_JSONLD_converter.py`: This script handles the actual conversion of SPASE JSON to schema.org compatible JSON-LD.
2. `HPDE_crawler.py`: This script crawls through the HPDE (Heliophysics Data Environment) directory structure, identifies SPASE JSON files, and applies the conversion process based on the specified data types.

The conversion maps SPASE metadata fields to appropriate schema.org types and properties, ensuring that the rich information contained in SPASE records is accurately represented in the resulting JSON-LD.

## SPASE to ODIS Mapping

To facilitate the conversion process and ensure consistency, we have created a mapping between SPASE metadata fields and their corresponding ODIS (schema.org) properties. This mapping serves as a reference for understanding how SPASE concepts are translated into the ODIS framework.

You can find the SPASE to ODIS mapping file here:
[SPASE_to_ODIS_mapping.md](./SPASE_to_ODIS_mapping.md)

## Helio-KNOW: Advancing Heliophysics through Open Science and Knowledge Commons

### Project Overview

The Helio-KNOW project aims to build a knowledge commons for managing heliophysics metadata and fostering scientific discovery. This initiative is part of a multi-year effort involving several organizations, including NASA Jet Propulsion Laboratory, the Center for Astrophysics (Harvard and Smithsonian), and Paris Observatory.

#### Key Objectives:
- Integrate data and research results from diverse sources in heliophysics
- Enable collaboration across different scales, labs, and organizations
- Advance understanding of complex phenomena like magnetosphere-ionosphere coupling
- Support future space missions and improve space weather predictions

### The Importance of Open Science in Heliophysics

Heliophysics, the study of the solar system and its effects on our lives, climate, and space technology, stands to benefit significantly from open science principles. The field encompasses various disciplines and produces vast amounts of data from multiple sources, making data integration and collaboration crucial for advancing our understanding of the solar system.

### Benefits for Helio-KNOW

This conversion process is a key component of the Helio-KNOW project, which aims to build a knowledge commons for heliophysics. By converting SPASE metadata to ODIS format, we're taking a significant step towards:

- Integrating heliophysics data with broader scientific datasets
- Enabling more effective collaboration across different scales and organizations
- Supporting future space missions and improving space weather predictions through enhanced data accessibility and interoperability

### ODIS Project Integration

The Ocean Data and Information System (ODIS) architecture is being adapted for use in the Helio-KNOW project. This integration aims to provide a schema.org-based interoperability layer, enabling effective development and dissemination of digital technology and sharing of heliophysics data, information, and knowledge.

#### Key Features of ODIS Architecture:
- Uses web architecture to expose structured data using schema.org vocabulary
- Enables interoperability between existing and emerging data systems
- Facilitates discovery through major commercial indexes and domain-focused groups

## How to Use This Repository

This repository contains tools to convert SPASE (Space Physics Archive Search and Extract) metadata to JSON-LD format compatible with schema.org vocabulary. Here's how to use the provided scripts:

### Prerequisites
- Python 3.7 or higher
- Required Python packages: `json`, `datetime`, `os`, `xml.etree.ElementTree`, `urllib`

### Configuration

1. **Mapping Specification:**
   - The mapping specification is defined in a YAML file (`mapping_spec.yaml`). This file contains the mappings between SPASE metadata fields and schema.org properties.
   - Example of `mapping_spec.yaml`:
     ```yaml
     common_mappings: &common_mappings
       ResourceID:
         targets:
           - "@id"
           - "url"
         transform: "to_url"
       ResourceHeader.ResourceName:
         target: "name"
         transform: null
       ResourceHeader.ReleaseDate:
         target: "sdDatePublished"
         transform: "extract_date"
       ResourceHeader.Description:
         targets:
           - "description"
           - "abstract"
         transform: null
       ObservedRegion:
         target: "spatialCoverage"
         transform: "map_to_place"
       Keyword:
         target: "keywords"
         transform: null
       AccessInformation.AccessURL:
         target: "distribution"
         transform: "map_distribution"

     DisplayData:
       mappings:
         <<: *common_mappings

     NumericalData:
       mappings:
         <<: *common_mappings
         Parameter:
           target: "variableMeasured"
           transform: "map_parameters"
     ```

2. **Updating the Mapping Specification:**
   - To add a new mapping or data type, update the `mapping_spec.yaml` file with the new mappings.
   - Example of adding a new data type:
     ```yaml
     NewDataType:
       mappings:
         <<: *common_mappings
         NewField:
           target: "newProperty"
           transform: "new_transform_function"
     ```

### Running the Code

1. Clone this repository:
   ```bash
   git clone https://github.com/your-repo/helio-know-odis.git
   cd helio-know-odis
   ```

2. Ensure your SPASE JSON files are in the `../hpde.io` directory (or modify the `root_dir` in `HPDE_crawler.py` accordingly).

3. Specify the desired data types to process in the `datatypes` variable in the `main` function of `HPDE_crawler.py`. For example:
   ```python:HPDE_crawler.py
   startLine: 86
   endLine: 87
   ```

4. Run the HPDE crawler:
   ```bash
   python HPDE_crawler.py
   ```

This script will:
- Crawl the HPDE file directory
- Process JSON files in the specified subdirectories
- Convert SPASE metadata to JSON-LD format
- Store the resulting JSON-LD files in the `./ODIS_JSONLD` directory
- Update the `sitemap.xml` file with new entries

### Adding a New Mapping / Data Type

1. **Update `mapping_spec.yaml`:**
   - Add the new data type and its mappings to the `mapping_spec.yaml` file.
   - Example:
     ```yaml
     NewDataType:
       mappings:
         <<: *common_mappings
         NewField:
           target: "newProperty"
           transform: "new_transform_function"
     ```

2. **Implement the Transformation Function:**
   - If the new mapping requires a new transformation function, implement it in the `mapping_engine.py` file.
   - Example:
     ```python:mapping_engine.py
     startLine: 1
     endLine: 20
     ```

3. **Run the HPDE Crawler:**
   - Ensure the new data type is included in the `datatypes` variable in `HPDE_crawler.py`.
   - Run the crawler to process the new data type.