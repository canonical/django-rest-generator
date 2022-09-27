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
        return cls._request("GET", url=url, params=params)


class ListableAPIResourceMixin:
    @classmethod
    def list(
        cls,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.class_url()
        return cls._request("GET", url=url, params=params)


class CreateableAPIResourceMixin:
    @classmethod
    def create(
        cls,
        data: Optional[dict] = None,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.class_url()
        return cls._request("POST", url=url, json=data, params=params)


class UpdateableAPIResourceMixin:
    @classmethod
    def update(
        cls,
        object_id: Toid,
        data: Optional[dict] = None,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.instance_url(object_id)
        return cls._request("PUT", url=url, json=data, params=params)


class PartiallyUpdateableAPIResourceMixin:
    @classmethod
    def partial_update(
        cls,
        object_id: Toid,
        data: Optional[dict] = None,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.instance_url(object_id)
        return cls._request("PATCH", url=url, json=data, params=params)


class DeletableAPIResourceMixin:
    @classmethod
    def delete(
        cls,
        object_id: Toid,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.instance_url(object_id)
        return cls._request("DELETE", url=url, params=params)


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
        response = cls.list(params=dict(_params, page=1))
        yield response, 1  # yield first page
        total_pages = response.data.get("total_pages", 1)
        for page in range(2, total_pages + 1):
            response = cls.list(params=dict(_params, page=page))
            yield response, page  # yield subsequent pages


class SingletonAPIResourceMixin:
    @classmethod
    def get(
        cls,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.class_url()
        return cls._request("GET", url=url, params=params)

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
