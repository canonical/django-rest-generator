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
from django_rest_generator.utils import (
    sanitize_endpoint_to_method_name,
    find_nested_keys,
    match_to_openapi_path_spec,
)


@pytest.mark.parametrize(
    "test_input, expected",
    [
        pytest.param("api/v2/bugs", "api.v2.bugs"),
        pytest.param("api/v2/projects/", "api.v2.projects"),
        pytest.param("/api/v2/bugs/", ".api.v2.bugs"),
        pytest.param("api/v2/hot-bugs/", "api.v2.hot-bugs"),
    ],
)
def test_sanitize_endpoint_to_method_name(test_input, expected):
    assert sanitize_endpoint_to_method_name(test_input) == expected


@pytest.mark.parametrize(
    "node, key, expected",
    [
        pytest.param({"id": "12", "item1": {"ref": "itemref"}}, "ref", ["itemref"]),
        pytest.param(
            {
                "id": "13",
                "items": [
                    {"id": "item1", "ref": "item1ref"},
                    {"id": "item2", "ref": "item2ref"},
                ],
            },
            "ref",
            ["item1ref", "item2ref"],
        ),
    ],
)
def test_find_nested_keys(node, key, expected):
    assert list(find_nested_keys(node, key)) == expected


@pytest.mark.parametrize(
    "openapi_path, request_path, expected",
    [
        pytest.param("{id}/", "12/", True),
        pytest.param("{id}/cancel", "12/cancel", True),
        pytest.param("{id}/cancel", "12/", False),
        pytest.param("/", "12/", False),
        pytest.param("/", "/", True),
        pytest.param("hotbugs/", "12/", False),
        pytest.param(
            "{id}/",
            "hotbugs/",
            False,
            marks=pytest.mark.xfail(
                reason="""Regex cant differentiate between number only patters and all character patters as there is no
                context on the OpenApi schema to infer this.""",
                strict=True,  # Let us know if this somehow gets fixed accidentaly.
            ),
        ),  # This one is known to fail due to how we do matching.
    ],
)
def test_match_to_openapi_path_spec(openapi_path, request_path, expected):
    assert match_to_openapi_path_spec(openapi_path, request_path) == expected
