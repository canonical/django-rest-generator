# BSD 3-Clause License

# Copyright (c) 2021, Certego S.R.L
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import inspect
import requests
import logging
from abc import ABCMeta, abstractmethod
from typing import Dict, Union, Optional
import re
from .utils import sanitize_endpoint_to_method_name
from .mixins import (
    CreateableAPIResourceMixin,
    DeletableAPIResourceMixin,
    ListableAPIResourceMixin,
    PaginationAPIResourceMixin,
    PartiallyUpdateableAPIResourceMixin,
    RetrievableAPIResourceMixin,
    SingletonAPIResourceMixin,
    UpdateableAPIResourceMixin,
)
from .response import APIResponse
from .resource import APIResource
from .exceptions import APIClientException
from .types import TRequestMethods, THeaders, TParams
from openapi_parser import parse
from collections import defaultdict


class APIClient(metaclass=ABCMeta):
    """
    Abstract ``APIClient`` class.
    Should be subclassed overwriting the ``_server_url``, ``_headers`` properties
    and attaching ``APIResource`` classes.
    """

    _logger: logging.Logger = logging.getLogger(__name__)
    _open_api_schema_endpoint: str = "openapi"

    def __init__(
        self,
        token: str,
        certificate: str = None,
        logger: logging.Logger = None,
    ):
        self.__token = token
        self.__certificate = certificate
        if logger is not None:
            self._logger = logger

        # hook
        self.__post__init__()

    def __post__init__(self) -> None:
        """
        Hook method for post ``__init__`` initialization.
        Always call ``super()`` if overwriting this.
        """
        # register resources predefined on the base class.
        for key, klass in self._get_resources_map().items():
            self.register_resource(key, klass)

    def register_resource(self, atrribute, manager_class):
        manager_class._request = self._request
        self.__setattr__(atrribute, manager_class)

    @property
    @abstractmethod
    def _server_url(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def _server_api_base(self) -> str:
        raise NotImplementedError()

    @property
    def _headers(self) -> THeaders:
        return {
            "Authorization": f"Token {self.__token}",
            "User-Agent": f"APIClient (weeblclient,v2)",
        }

    @property
    def __session(self) -> requests.Session:
        """
        Internal use only.
        """
        if not hasattr(self, "__cached_session"):
            session = requests.Session()
            if self.__certificate is not None:
                session.verify = self.__certificate
            session.headers.update(self._headers)
            self.__cached_session = session

        return self.__cached_session

    def _request(
        self,
        method: TRequestMethods,
        url: str,
        *args,
        **kwargs,
    ) -> APIResponse:
        """
        For internal use only.
        """
        full_url = f"{self._server_url}/{url}"
        response: requests.Response = None
        try:
            response = self.__session.request(
                method=method, url=full_url, *args, **kwargs
            )
            self._logger.debug(
                msg=(response.url, response.status_code, response.content)
            )
            response.raise_for_status()
        except requests.RequestException as e:
            raise APIClientException(e, response=response)

        return APIResponse(response)

    def _get_resources_map(self) -> Dict[str, APIResource]:
        """
        Returns a dictionary mapping of ``APIResource`` classes attached to this ``APIClient`` instance.
        """
        inst_attrs = self.__dict__
        cls_attrs = type(self).__dict__

        # flake8: noqa: E731
        is_apiresource = lambda x: inspect.isclass(x) and issubclass(x, APIResource)
        inst_resources = {
            key: value for key, value in inst_attrs.items() if is_apiresource(value)
        }
        cls_resources = {
            key: value for key, value in cls_attrs.items() if is_apiresource(value)
        }
        cls_resources.update(inst_resources)
        return cls_resources

    @staticmethod
    def _make_resource_class(custom_actions, mixins):
        class DynamicResource(APIResource, *custom_actions, *mixins):
            pass

        return DynamicResource

    @staticmethod
    def _make_custom_action_class(custom_endpoint, custom_method, custom_detail):
        class DynamicCustomAction:
            def _run(
                cls, objectId: Union[str, int] = None, params: Optional[TParams] = None
            ) -> APIResponse:
                # Injected dynamically from upper level func
                method = custom_method
                detail = custom_detail
                endpoint = custom_endpoint

                # TODO: warn user when endpoint is not detail and he passess an objectId or reverse
                if detail and objectId:
                    base_url = cls.instance_url(objectId)
                else:
                    base_url = cls.class_url()

                url = f"{base_url}/{endpoint}"
                return cls._request(method, url=url, params=params)

        setattr(
            DynamicCustomAction,
            sanitize_endpoint_to_method_name(custom_endpoint),
            classmethod(getattr(DynamicCustomAction, "_run")),
        )
        delattr(DynamicCustomAction, "_run")
        return DynamicCustomAction

    def _parse_resources_from_openapi(self, spec):
        resources = defaultdict(lambda: defaultdict(list))
        for path in spec.paths:
            path_base = path.url.strip().replace(f"/{self._server_api_base}", "")
            path_methods = [x.method.value.upper() for x in path.operations]
            resource, endpoint = path_base.split("/", maxsplit=1)
            if endpoint == "":
                endpoint = "/"
            resources[resource][endpoint].extend(path_methods)
        return resources

    def _build_resource_object(self, resource_name: str, endpoints: dict):
        is_detail_action = lambda x: re.match(r"{.*}\/", x) is not None
        instance_method_map = {
            "GET": [RetrievableAPIResourceMixin, SingletonAPIResourceMixin],
            "PUT": [UpdateableAPIResourceMixin],
            "DELETE": [DeletableAPIResourceMixin],
            "PATCH": [PartiallyUpdateableAPIResourceMixin],
        }
        object_method_map = {
            "POST": [CreateableAPIResourceMixin],
            "GET": [ListableAPIResourceMixin, PaginationAPIResourceMixin],
        }

        resource_mixins = set()
        custom_actions = set()
        for endpoint, methods in endpoints.items():
            if endpoint == "/":
                # It is a root object or a singleton
                for method in methods:
                    resource_mixins.update(object_method_map[method])
            elif re.match(r"{.*}\/$", endpoint) is not None:
                # It is an instance/object endpoint
                for method in methods:
                    resource_mixins.update(instance_method_map[method])

            else:
                # We are a custom action here
                # A custom action must only have one method.
                if len(methods) > 1:
                    raise Warning(
                        f"Custom action at {resource_name}/{endpoint} has more than the ONE allowed HTTP method: {methods}."
                    )
                custom_action_name = re.sub(r"{.*}\/", "", endpoint)
                custom_actions.add(
                    self._make_custom_action_class(
                        custom_action_name, methods[0], is_detail_action(endpoint)
                    )
                )

        resource_class = self._make_resource_class(custom_actions, resource_mixins)

        resource_class.OBJECT_NAME = f"{self._server_api_base}{resource_name}"
        return resource_class

    def _build_from_openapi_schema(self, schema_file: str = None):
        schema = f"{self._server_url}/{self._open_api_schema_endpoint}"
        if schema_file is not None:
            schema = schema_file

        spec = parse(schema)
        resources = self._parse_resources_from_openapi(spec=spec)

        for resource, endpoints in resources.items():
            resource_class = self._build_resource_object(resource, endpoints)
            self.register_resource(resource, resource_class)

    @classmethod
    def build_from_openapi_schema(cls, schema_file, token=None):
        return cls(token=token)._build_from_openapi_schema(schema_file)


class GenericApiClient(APIClient):
    def __init__(self, server_url, api_base, schema_endpoint, *args, **kwargs):
        self.__server_url = server_url
        self.__server_api_base = api_base
        self.__open_api_schema_endpoint = schema_endpoint
        super().__init__(*args, **kwargs)

    @property
    def _server_url(self) -> str:
        return self.__server_url

    @property
    def _server_api_base(self) -> str:
        return self.__server_api_base

    @property
    def _open_api_schema_endpoint(self):
        return self.__open_api_schema_endpoint
