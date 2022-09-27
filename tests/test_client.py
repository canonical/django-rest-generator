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


def test_client_loads_static_resources(client_class_mock, api_token):
    client = client_class_mock(token=api_token)

    assert hasattr(client, "TestResource")
    assert hasattr(client.TestResource, "OBJECT_NAME")


def test_client_uses_specified_logger(client_class_mock, api_token):
    import logging

    logger = logging.getLogger("test")
    client = client_class_mock(token=api_token, logger=logger)
    assert client._logger == logger
