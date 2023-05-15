# Copyright (C) 2022 Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from dataclasses import dataclass, make_dataclass
from typing import List, Dict
from prance import ResolvingParser, BaseParser
from prance.util.resolver import RESOLVE_HTTP, RESOLVE_FILES, RESOLVE_INTERNAL
from collections import defaultdict
from django_rest_generator.parser.models import (
    Schema,
    CommonDataclass,
    EndpointOperation,
    Endpoint,
    Resource,
)
from django_rest_generator.utils import find_nested_keys, schema_to_dataclass


def _build_resource_objects(raw_resources: dict) -> List[Resource]:
    output_resources = list()
    for resource, endpoints in raw_resources.items():
        resource_endpoints = []
        for endpoint_path, endpoint_operations in endpoints.items():
            ep = Endpoint(path=endpoint_path, operations=endpoint_operations)
            resource_endpoints.append(ep)
        res = Resource(name=resource, endpoints=resource_endpoints)
        output_resources.append(res)

    return output_resources


def _parse_resource_objects_from_openapi(
    specification: dict, server_base: str
) -> defaultdict[str, defaultdict[str, List[EndpointOperation]]]:
    resources = defaultdict(lambda: defaultdict(list))

    for path_url, operations in specification["paths"].items():
        path_base = path_url.strip().replace(f"/{server_base}", "")
        path_methods = []

        resource, endpoint = path_base.split("/", maxsplit=1)
        if endpoint == "":
            endpoint = "/"

        for path_method_name, path_method_data in operations.items():
            # path_schema = set(
            #     find_nested_keys(
            #         list(find_nested_keys(path_method_data["responses"], "schema")),
            #         "$ref",
            #     )
            # )
            path_schema = list(
                find_nested_keys(path_method_data["responses"], "schema")
            )
            path_schema = path_schema.pop() if path_schema else dict()
            path_schema_class = schema_to_dataclass(
                f"{resource}@{endpoint}", path_schema, CommonDataclass
            )
            path_schema = path_schema_class(**path_schema.get("properties", {}))
            endpoint_op = EndpointOperation(
                return_type=path_schema, method=path_method_name.upper()
            )
            path_methods.append(endpoint_op)

        resources[resource][endpoint].extend(path_methods)

    return resources


@dataclass
class OpenAPISpec:
    schemas: Dict[str, Schema]
    resources: List[Resource]

    @staticmethod
    def _parse_resources_from_openapi(specification, server_base):
        raw_resources = _parse_resource_objects_from_openapi(
            specification=specification, server_base=server_base
        )
        parsed_resources = _build_resource_objects(raw_resources=raw_resources)
        return parsed_resources

    @staticmethod
    def _parse_schemas_from_spec(specification):
        schemas = dict()
        conversion_table = {
            "array": list,
            "string": str,
            "boolean": bool,
            "integer": int,
            "number": float,
            "object": object,
        }
        schema_components = specification.get("components", {}).get("schemas", {})
        if len(schema_components) < 1:
            print("ERROR: No schema components found in OpenAPI definition.")
            return schemas

        for schema_name, schema in schema_components.items():
            data_class_fields = [
                (field_name, conversion_table[field_data["type"]])
                for field_name, field_data in schema["properties"].items()
            ]
            data_class = make_dataclass(
                schema_name, data_class_fields, bases=(CommonDataclass,)
            )
            schemas[schema_name.lower()] = data_class

        return schemas

    @classmethod
    def parse(cls, schema, server_base):
        parser = ResolvingParser(
            schema, resolve_types=RESOLVE_HTTP | RESOLVE_FILES | RESOLVE_INTERNAL
        )
        # parser = BaseParser(schema,lazy=False)
        spec = parser.specification
        schemas = cls._parse_schemas_from_spec(spec)
        resources = cls._parse_resources_from_openapi(spec, server_base)
        return cls(schemas=schemas, resources=resources)
