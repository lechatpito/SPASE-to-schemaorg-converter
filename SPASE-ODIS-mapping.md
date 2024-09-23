# Mapping for the DisplayData type

| Source SPASE Term | Target ODIS/Schema.org Term | Notes |
|-------------------|---------------------------|-------|
| ResourceID | @id | Converted to <https://hpde.io/> URL |
| ResourceHeader.ResourceName | name | Direct mapping |
| ResourceHeader.ResourceName | creditText | Generated from ResourceName |
| ResourceHeader.Contact.PersonID | publisher.identifier | Direct mapping |
| ResourceHeader.ReleaseDate | sdDatePublished | Only date part is used |
| AccessInformation.AccessURL[0].URL | distribution.contentUrl | Using the third AccessURL for file listing |
| AccessInformation.Format | distribution.encodingFormat | Direct mapping |
| ResourceID | identifier | Direct mapping |
| ResourceHeader.Description | description | |
| ResourceHeader.Description | abstract | Used in addition to description |
| TemporalDescription.TimeSpan.StartDate | temporalCoverage | Converted to start date/... format |
| MeasurementType | variableMeasured | Direct mapping |
| ObservedRegion | spatialCoverage | Mapped to Place objects |
| Keyword | keywords | Direct mapping |
| - | license | Hardcoded value |
| - | audience | Hardcoded value |
| - | sdPublisher | Hardcoded value |
| - | includedInDataCatalog | Hardcoded value |
| AccessInformation.AccessURL[0].URL | distribution.contentUrl | Using the first AccessURL |
| InstrumentID | - | Not currently mapped |
| DisplayCadence | - | Not currently mapped |
| Caveats | - | Not currently mapped |

# Mapping for the NumericalData type


