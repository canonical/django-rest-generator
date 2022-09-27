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

import re


def sanitize_endpoint_to_method_name(endpoint):
    endpoint = str(endpoint).lower().strip()
    endpoint = re.sub(r"{.*}\/", "", endpoint)
    endpoint = endpoint.replace("/", ".")
    if endpoint.endswith("."):
        endpoint = endpoint[:-1]
    return endpoint
