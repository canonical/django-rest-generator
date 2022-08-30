
from django_rest_generator.client import APIClient
from .resources import SiloResource


class V2WeeblClient(APIClient):
    # overwrite
    _server_url: str = "http://localhost:8080"
    _server_api_base = "api/v2/"
    _open_api_schema_endpoint: str = "api/v2/openapi/"

    # Static resources can be directly attached here, 
    # others will be automatically injected

    SiloResource = SiloResource

if __name__ == "__main__":
    client = V2WeeblClient.build_from_openapi_schema(token="asdasdasd", schema="")