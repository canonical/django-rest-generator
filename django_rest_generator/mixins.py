# Copyright (C) 2022-2023 Canonical Ltd

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
import logging

LOGGER = logging.getLogger(__name__)


class RetrievableAPIResourceMixin:
    @classmethod
    def retrieve(
        cls,
        object_id: Toid,
        params: Optional[TParams] = None,
        logger: logging.Logger = LOGGER,
    ) -> APIResponse:
        url = cls.instance_url(object_id)
        logger.debug(f"[retrieve] Making GET request to {url} with parameters {params}")
        return cls.make_request("GET", url=url, params=params)


class ListableAPIResourceMixin:
    @classmethod
    def list(
        cls,
        params: Optional[TParams] = None,
        logger: logging.Logger = LOGGER,
    ) -> APIResponse:
        url = cls.class_url()
        logger.debug(f"[list] Making GET request to {url} with parameters {params}")
        return cls.make_request("GET", url=url, params=params)


class CreateableAPIResourceMixin:
    @classmethod
    def create(
        cls,
        data: Optional[dict] = None,
        params: Optional[TParams] = None,
        logger: logging.Logger = LOGGER,
    ) -> APIResponse:
        url = f"{cls.class_url()}/"
        logger.debug(
            f"[create] Making POST request to {url} with parameters {params} and data {data}"
        )
        return cls.make_request("POST", url=url, json=data, params=params)


class UpdateableAPIResourceMixin:
    @classmethod
    def update(
        cls,
        object_id: Toid,
        data: Optional[dict] = None,
        params: Optional[TParams] = None,
        logger: logging.Logger = LOGGER,
    ) -> APIResponse:
        url = cls.instance_url(object_id)
        logger.debug(
            f"[update] Making PUT request to {url} with parameters {params} and data {data}"
        )
        return cls.make_request("PUT", url=url, json=data, params=params)


class PartiallyUpdateableAPIResourceMixin:
    @classmethod
    def partial_update(
        cls,
        object_id: Toid,
        data: Optional[dict] = None,
        params: Optional[TParams] = None,
        logger: logging.Logger = LOGGER,
    ) -> APIResponse:
        url = cls.instance_url(object_id)
        logger.debug(
            f"[partial_update] Making PATCH request to {url} with parameters {params} and data {data}"
        )
        resp = cls.make_request("PATCH", url=url, json=data, params=params)
        if resp._response.ok:
            logger.debug("[partial_update] Successful")
        else:
            raise ValueError("Partial update failed")
        return resp


class DeletableObjectResourceMixin:
    @classmethod
    def delete(
        cls,
        params: Optional[TParams] = None,
        logger: logging.Logger = LOGGER,
    ) -> APIResponse:
        url = cls.class_url()
        logger.debug(
            f"[delete] Making DELETE request to {url} with parameters {params}"
        )
        return cls.make_request("DELETE", url=url, params=params)


class DeletableAPIResourceMixin:
    @classmethod
    def delete(
        cls,
        object_id: Toid,
        params: Optional[TParams] = None,
        logger: logging.Logger = LOGGER,
    ) -> APIResponse:
        url = cls.instance_url(object_id)
        logger.debug(
            f"[delete] Making DELETE request to {url} with parameters {params}"
        )
        return cls.make_request("DELETE", url=url, params=params)


class PaginationAPIResourceMixin:
    """
    Should be used with ``ListableAPIResourceMixin``.
    """

    @classmethod
    def all(
        cls,
        params: Optional[TParams] = None,
        logger: logging.Logger = LOGGER,
    ) -> Generator[Tuple[APIResponse, int], None, None]:
        _params = params or {}  # default value
        logger.debug(f"[all] Getting all object from {cls} with parameters {params}")
        has_next = True

        while has_next:
            response = cls.list(params=dict(_params), logger=logger)

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
        logger: logging.Logger = LOGGER,
    ) -> APIResponse:
        url = cls.class_url()
        logger.debug(f"[get] Making GET request to {url} with parameters {params}")
        obj = cls.make_request("GET", url=url, params=params)
        if len(obj.results) > 1:
            raise ValueError("Got more than one object back from request.")
        elif len(obj.results) < 1:
            return None
        return obj.results[0]

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


class GetOrCreateAPIResourceMixin:
    @classmethod
    def get_or_create(
        cls,
        params: TParams,
        data: dict,
        logger: Optional[logging.Logger] = LOGGER,
    ):
        """Gets the specified item filtering by the `params` key
        or creates it using the `data` key."""
        obj = cls.get(params=params, logger=logger)

        if obj is None:
            logger.debug("[get_or_create] Got no results back from request, creating.")
            return cls.create(data=data, logger=logger).data
        else:
            # It existed so we only return that one.
            return obj
