# Copyright (C) 2022 Canonical Ltd

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pytest
from django_rest_generator.client import APIClient
from django_rest_generator.resource import APIResource
from django_rest_generator.mixins import (
    CreateableAPIResourceMixin,
    DeletableAPIResourceMixin,
    ListableAPIResourceMixin,
    PaginationAPIResourceMixin,
    PartiallyUpdateableAPIResourceMixin,
    RetrievableAPIResourceMixin,
    SingletonAPIResourceMixin,
    UpdateableAPIResourceMixin,
)


@pytest.fixture(scope="session")
def server_url():
    yield "http://localhost:8081"


@pytest.fixture(scope="session")
def server_api_base():
    yield "api/v2/"


@pytest.fixture(scope="session")
def open_api_schema_endpoint():
    yield "api/v2/openapi/"


@pytest.fixture(scope="session")
def endpoint_object_name():
    yield "api.v2.silos"


@pytest.fixture(scope="session")
def api_token():
    yield "developmentttokenhere"


@pytest.fixture(scope="function")
def resource_class_all_mixins(endpoint_object_name):
    class MockResourceClass(
        APIResource,
        CreateableAPIResourceMixin,
        DeletableAPIResourceMixin,
        ListableAPIResourceMixin,
        PaginationAPIResourceMixin,
        PartiallyUpdateableAPIResourceMixin,
        RetrievableAPIResourceMixin,
        SingletonAPIResourceMixin,
        UpdateableAPIResourceMixin,
    ):
        OBJECT_NAME = endpoint_object_name

    yield MockResourceClass


@pytest.fixture(scope="function")
def client_class_mock(
    server_url, server_api_base, open_api_schema_endpoint, resource_class_all_mixins
):
    class MockApiClient(APIClient):
        _server_url = server_url
        _server_api_base = server_api_base
        _open_api_schema_endpoint = open_api_schema_endpoint

        TestResource = resource_class_all_mixins

    yield MockApiClient


@pytest.fixture(scope="function")
def bad_client_class_mock(server_url, server_api_base, open_api_schema_endpoint):
    class BadMockApiClient(APIClient):
        _server_url = server_url
        _server_api_base = server_api_base
        _open_api_schema_endpoint = open_api_schema_endpoint

        TestResource = APIResource

    yield BadMockApiClient
