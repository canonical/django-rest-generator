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

import requests
import json
from typing import Union
from requests.models import CaseInsensitiveDict
from django_rest_generator.parser.models import Schema


class APIResponse(object):
    response: requests.Response
    url: str
    code: int
    headers: CaseInsensitiveDict
    data: dict
    file_name: str
    raw: bytes

    def __init__(self, response: requests.Response, schema: Schema = None) -> None:
        self._response = response
        self.url = response.url
        self.code = response.status_code
        self.headers = response.headers
        self._schema = schema
        try:
            self._handle_json_response()
        except json.JSONDecodeError:
            self._handle_generic_response()

    def _handle_json_response(self) -> None:
        self.data = self._response.json()
        if self._schema is not None:
            self.data = self._schema.from_dict(self.data)

    def _handle_generic_response(self) -> None:
        content_disposition = self._response.headers.get("Content-Disposition", "")
        _split_names = content_disposition.split(r"attachment; filename=")
        if len(_split_names) == 2:
            # case: file attachment
            self.file_name = _split_names[1]
            self.raw = self._response.content

    @property
    def results(self) -> Union[list, dict]:
        return self.data["results"]

    @property
    def next_url(self) -> Union[str, None]:
        return self.data["next"]

    @property
    def has_next_url(self) -> bool:
        return self.next_url is not None

    def __repr__(self) -> str:
        return f'APIResponse({self._schema}, "{self.url}", {self.code})'
