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
from django_rest_generator.parser import OpenAPISpec
from django_rest_generator.parser.models import CommonDataclass
from dataclasses import dataclass


def test_OpenAPISpec_class():
    schema = OpenAPISpec.parse("tests/data/open-api-schema.yaml", "api/v2/")
    assert len(schema.schemas) == 44  # There are 44 schemas in the yaml file.


def test_models_as_dict_from_dict():
    @dataclass
    class TestModel(CommonDataclass):
        test_field: str

    test_dict = {"test_field": 12342, "other_field": "hello"}

    assert TestModel.from_dict(test_dict) == TestModel(
        test_field=test_dict["test_field"]
    )
    assert TestModel.from_dict(test_dict).as_dict() == {
        "test_field": test_dict["test_field"]
    }


def test_resource_model_get_schema():
    schema = OpenAPISpec.parse("tests/data/open-api-schema.yaml", "api/v2/")
    users_resource = schema.resources[0]
    assert users_resource.get_schema("me/", "GET") == "User"
    assert users_resource.get_schema("i/dont/exists", "POST") == None
    assert users_resource.get_schema("12/", "PUT") == "User"


def test_parser_no_schemas(capsys):
    empty_test_schema = {"components": {"schemas": {}}}

    OpenAPISpec._parse_schemas_from_spec(empty_test_schema)
    assert "ERROR: No schema components found" in capsys.readouterr().out
