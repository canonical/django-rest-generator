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

from typing import Tuple, Optional, Generator
from urllib.parse import urlparse, parse_qsl
from .response import APIResponse
from .types import Toid, TParams


class RetrievableAPIResourceMixin:
    @classmethod
    def retrieve(
        cls,
        object_id: Toid,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.instance_url(object_id)
        return cls.make_request("GET", url=url, params=params)


class ListableAPIResourceMixin:
    @classmethod
    def list(
        cls,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.class_url()
        return cls.make_request("GET", url=url, params=params)


class CreateableAPIResourceMixin:
    @classmethod
    def create(
        cls,
        data: Optional[dict] = None,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = f"{cls.class_url()}/"
        return cls.make_request("POST", url=url, json=data, params=params)


class UpdateableAPIResourceMixin:
    @classmethod
    def update(
        cls,
        object_id: Toid,
        data: Optional[dict] = None,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.instance_url(object_id)
        return cls.make_request("PUT", url=url, json=data, params=params)


class PartiallyUpdateableAPIResourceMixin:
    @classmethod
    def partial_update(
        cls,
        object_id: Toid,
        data: Optional[dict] = None,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.instance_url(object_id)
        return cls.make_request("PATCH", url=url, json=data, params=params)


class DeletableObjectResourceMixin:
    @classmethod
    def delete(
        cls,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.class_url()
        return cls.make_request("DELETE", url=url, params=params)


class DeletableAPIResourceMixin:
    @classmethod
    def delete(
        cls,
        object_id: Toid,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.instance_url(object_id)
        return cls.make_request("DELETE", url=url, params=params)


class PaginationAPIResourceMixin:
    """
    Should be used with ``ListableAPIResourceMixin``.
    """

    @classmethod
    def all(
        cls,
        params: Optional[TParams] = None,
    ) -> Generator[Tuple[APIResponse, int], None, None]:

        _params = params or {}  # default value
        has_next = True

        while has_next:
            response = cls.list(params=dict(_params))

            for item in response.results:
                yield item

            if response.has_next_url:
                o = urlparse(response.next_url)
                next_query_params = parse_qsl(o.query)
                for param in next_query_params:
                    _params[param[0]] = param[1]
            else:
                has_next = False


class SingletonAPIResourceMixin:
    @classmethod
    def get(
        cls,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.class_url()
        return cls.make_request("GET", url=url, params=params)

    @classmethod
    def class_url(cls) -> str:
        if cls == SingletonAPIResourceMixin:
            raise NotImplementedError(
                "SingletonAPIResource is an abstract class."
                " You should perform actions on its subclasses ."
            )
        # Namespaces are separated in object names with periods (.) and in URLs
        # with forward slashes (/), so replace the former with the latter.
        base = cls.OBJECT_NAME.replace(".", "/")
        return base

    @classmethod
    def instance_url(cls) -> str:
        return cls.class_url()
