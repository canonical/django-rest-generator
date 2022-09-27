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


def test_client_resource_generates_correct_class_url(client_class_mock, api_token):
    client = client_class_mock(token=api_token)
    assert client.TestResource.class_url() == "api/v2/silos"


def test_client_resource_generates_correct_instance_url(client_class_mock, api_token):
    client = client_class_mock(token=api_token)
    instance_id = 11

    assert (
        client.TestResource.instance_url(instance_id) == f"api/v2/silos/{instance_id}/"
    )


def test_client_resource_instance_url_bad_params(client_class_mock, api_token):
    client = client_class_mock(token=api_token)
    instance_id = None  # not a string or int
    with pytest.raises(RuntimeError) as raised_error:
        client.TestResource.instance_url(instance_id)

    assert "Could not determine which URL to request" in str(raised_error.value)


def test_client_resource_class_url_bad_resource(bad_client_class_mock, api_token):
    client = bad_client_class_mock(token=api_token)
    with pytest.raises(NotImplementedError) as raised_error:
        client.TestResource.class_url()
    assert "You should perform actions on its subclasses" in str(raised_error.value)
