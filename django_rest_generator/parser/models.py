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

from dataclasses import dataclass, fields, asdict, field
from typing import List, Union
from django_rest_generator.types import TRequestMethods
from django_rest_generator.utils import match_to_openapi_path_spec


class CommonDataclass:
    # Not really a dataclass but it doesn't have an __init__
    # method so all good.
    @classmethod
    def from_dict(cls, dictionary: dict):
        possible_keys = [field.name for field in fields(cls)]
        filtered_dict = {k: v for k, v in dictionary.items() if k in possible_keys}
        return cls(**filtered_dict)

    def as_dict(self):
        return asdict(self)


@dataclass
class Schema(CommonDataclass):
    required: List[str]


@dataclass
class EndpointOperation(CommonDataclass):
    return_type: str
    method: TRequestMethods


@dataclass
class Endpoint(CommonDataclass):
    path: str
    operations: List[EndpointOperation]


@dataclass
class Resource(CommonDataclass):
    name: str
    endpoints: List[Endpoint]

    def get_schema(self, path, method) -> Union[str, None]:
        for endpoint in self.endpoints:
            print(endpoint.path, path)
            if match_to_openapi_path_spec(endpoint.path, path):
                for ops in endpoint.operations:
                    if ops.method == method:
                        return ops.return_type


@dataclass
class Metadata(CommonDataclass):
    resource: Resource
    schema: Schema
