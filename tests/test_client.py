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

class MockClient(APIClient):
    @property
    def _server_url(self) -> str:
        return super()._server_url
    
    @property
    def _server_api_base(self) -> str:
        return super()._server_api_base
    

def test_client_loads_static_resources(client_class_mock, api_token):
    client = client_class_mock(token=api_token)

    assert hasattr(client, "TestResource")
    assert hasattr(client.TestResource, "OBJECT_NAME")


def test_client_uses_specified_logger(client_class_mock, api_token):
    import logging

    logger = logging.getLogger("test")
    client = client_class_mock(token=api_token, logger=logger)
    assert client._logger == logger

def test_client_sets_server_url(client_class_mock, api_token, server_url):
    client = client_class_mock(token=api_token)
    assert client._server_url == server_url


def test_abstract_client_raises_not_implemented_server_url(api_token):
    client = MockClient(token=api_token)
    with pytest.raises(NotImplementedError):
        # This should raise NotImplemented as our mock class just refers back to the abstract client
        client._server_url

def test_abstract_client_raises_not_implemented_server_api_base(api_token):
    client = MockClient(token=api_token)
    with pytest.raises(NotImplementedError):
        # This should raise NotImplemented as our mock class just refers back to the abstract client
        client._server_api_base

def test_client_sets_headers_as_dict(client_class_mock, api_token):
    client = client_class_mock(token=api_token)
    assert isinstance(client._headers, dict)