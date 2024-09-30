# YAML Mapping Documentation

## common_mappings Mappings

```yaml
common_mappings:
  AccessInformation.AccessURL:
    target: distribution
    transform: map_distribution
  Keyword:
    target: keywords
    transform: null
  ObservedRegion:
    target: spatialCoverage
    transform: map_to_place
  ResourceHeader.Description:
    targets:
    - description
    - abstract
    transform: null
  ResourceHeader.ReleaseDate:
    target: sdDatePublished
    transform: extract_date
  ResourceHeader.ResourceName:
    target: name
    transform: null
  ResourceID:
    targets:
    - '@id'
    - url
    transform: to_url
```

## DisplayData Mappings

```yaml
DisplayData:
  mappings:
    AccessInformation.AccessURL:
      target: distribution
      transform: map_distribution
    Keyword:
      target: keywords
      transform: null
    ObservedRegion:
      target: spatialCoverage
      transform: map_to_place
    ResourceHeader.Description:
      targets:
      - description
      - abstract
      transform: null
    ResourceHeader.ReleaseDate:
      target: sdDatePublished
      transform: extract_date
    ResourceHeader.ResourceName:
      target: name
      transform: null
    ResourceID:
      targets:
      - '@id'
      - url
      transform: to_url
```

## NumericalData Mappings

```yaml
NumericalData:
  mappings:
    AccessInformation.AccessURL:
      target: distribution
      transform: map_distribution
    Keyword:
      target: keywords
      transform: null
    ObservedRegion:
      target: spatialCoverage
      transform: map_to_place
    Parameter:
      target: variableMeasured
      transform: map_parameters
    ResourceHeader.Description:
      targets:
      - description
      - abstract
      transform: null
    ResourceHeader.ReleaseDate:
      target: sdDatePublished
      transform: extract_date
    ResourceHeader.ResourceName:
      target: name
      transform: null
    ResourceID:
      targets:
      - '@id'
      - url
      transform: to_url
```