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
    client = V2WeeblClient.build_from_openapi_schema(token="asdasdasd", schema_file="")
