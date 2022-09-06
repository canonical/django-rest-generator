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

from typing import Optional

from django_rest_client import (
    RetrievableAPIResourceMixin,
    ListableAPIResourceMixin,
    PaginationAPIResourceMixin,
    DeletableAPIResourceMixin,
    UpdateableAPIResourceMixin,
    SingletonAPIResourceMixin,
)
from django_rest_client.types import Toid, TParams
from weeblclient.weeblclient.v2.lib.api_resource import APIResource
from weeblclient.weeblclient.v2.lib.api_response import APIResponse


class SiloResource(
    APIResource,
    RetrievableAPIResourceMixin,
    ListableAPIResourceMixin,
    PaginationAPIResourceMixin,
    DeletableAPIResourceMixin,
    UpdateableAPIResourceMixin,
):
    """
    An Example resource. Suitable for DRF's ``ModelView``.
    """

    OBJECT_NAME = "api.v2.silos"

    @classmethod
    def custom_action(
        cls,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        """
        Suitable for ``@action`` decorator views with  ``detaile=False``.
        """
        url = cls.class_url() + "/custom-action"
        return cls._request("GET", url=url, params=params)

    @classmethod
    def custom_action_detailed(
        cls,
        object_id: Toid,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        """
        Suitable for ``@action`` decorator views with ``detaile=True``.
        """
        url = cls.instance_url(object_id) + "/custom-action-detailed"
        return cls._request("POST", url=url, params=params)