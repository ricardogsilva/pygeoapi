from pathlib import Path

from .schemas import internal


def get_config() -> internal.PyGeoApiConfig:
    """Returns a default configuration for pygeoapi."""
    return internal.PyGeoApiConfig(
        debug=False,
        language="en-US",
        pagination_limit=100,
        ogc_api_schemas_base_dir=str(Path.home() / "SCHEMAS_OPENGIS_NET/ogcapi"),
        validate_responses=True,
        metadata=internal.PyGeoApiMetadataConfig(
            identification=internal.PyGeoApiMetadataIdentificationConfig(
                title="pygeoapi default instance",
                description="pygeoapi provides an API to geospatial data",
                keywords=[
                    "geospatial",
                    "data",
                    "api",
                ],
                keywords_type="theme",
                terms_of_service="https://creativecommons.org/licenses/by/4.0/",
                url="https://example.org"
            ),
            license=internal.PyGeoApiMetadataLicenseConfig(
                name="CC-BY 4.0 license",
                url="https://creativecommons.org/licenses/by/4.0/",
            ),
            provider=internal.PyGeoApiMetadataProviderConfig(
                name="Organization Name",
                url="https://pygeoapi.io",
            ),
            point_of_contact=internal.PyGeoApiMetadataPointOfContactConfig(
                name="Lastname, Firstname",
                position="Position title",
                address="Mailing address",
                city="City",
                state_or_province="Administrative area",
                postal_code="Zip or postal code",
                country="Country",
                phone="+xx-xxx-xxx-xxxx",
                fax="+xx-xxx-xxx-xxxx",
                email="you@example.org",
                url="Contact URL",
                hours="Mo-Fr 08:00-17:00",
                instructions="During hours of service. Off on weekends.",
                role="pointOfContact",
            ),
        ),
    )
