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
from dataclasses import make_dataclass


def sanitize_endpoint_to_method_name(endpoint):
    endpoint = str(endpoint).lower().strip()
    endpoint = re.sub(r"{.*}\/", "", endpoint)
    endpoint = endpoint.replace("/", ".")
    if endpoint.endswith("."):
        endpoint = endpoint[:-1]
    return endpoint


def find_nested_keys(node, key):
    if isinstance(node, list):
        for i in node:
            for x in find_nested_keys(i, key):
                yield x
    elif isinstance(node, dict):
        if key in node:
            yield node[key]
        for j in node.values():
            for x in find_nested_keys(j, key):
                yield x


def match_to_openapi_path_spec(openapi_path, request_path) -> bool:
    """Match s against the given format string.

    Some examples here:
        OpenApi path, request URL path, expected result
        {id}/               12/             True
        {id}/cancel         12/cancel       True
        {id}/cancel         12/             False
        /                   12/             False


    Slightly modified from the source to better fit our use case.
    Source: https://stackoverflow.com/a/51878773
    """
    if openapi_path == request_path:
        # If they're the same, we don't need to process.
        return True

    # First split on any keyword arguments, note that the names of keyword arguments will be in the
    # 1st, 3rd, ... positions in this list
    tokens = re.split(r"\{(.*?)\}", openapi_path)
    keywords = tokens[1::2]

    # Now replace keyword arguments with named groups matching them. We also escape between keyword
    # arguments so we support meta-characters there. Re-join tokens to form our regexp pattern
    tokens[1::2] = map("(?P<{}>.+)".format, keywords)
    tokens[0::2] = map(re.escape, tokens[0::2])
    pattern = "".join(tokens)

    # Use our pattern to match the given string, return False if it doesn't match.
    # Use fullmatch to get better accuracy; I.e: should match the whole string, not just the beggining.
    matches = re.fullmatch(pattern, request_path)
    if not matches:
        return False

    # generate a dict with all of our keywords and their values
    substitutions = {x: matches.group(x) for x in keywords}
    model = openapi_path.format(**substitutions)
    return model == request_path


def schema_to_dataclass(schema_name, schema, dataclass_base):
    conversion_table = {
        "array": list,
        "string": str,
        "boolean": bool,
        "integer": int,
        "number": float,
        "object": object,
    }

    data_class_fields = [
        (field_name, conversion_table[field_data["type"]])
        for field_name, field_data in schema.get("properties", {}).items()
    ]
    data_class = make_dataclass(schema_name, data_class_fields, bases=(dataclass_base,))
    return data_class
