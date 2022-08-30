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