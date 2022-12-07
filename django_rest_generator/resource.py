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

from abc import ABCMeta
from typing import Callable

from .types import Toid


class APIResource(metaclass=ABCMeta):
    #: is injected during ``APIClient`` initialization.
    #: :meta private:
    _request: Callable
    OBJECT_NAME: str

    @classmethod
    def make_request(cls, http_method, url, *args, **kwargs):
        schema = cls.Meta.get_schema(url, http_method)
        return cls._request(http_method, url=url, return_schema=schema, *args, **kwargs)

    @classmethod
    def class_url(cls):
        """
        :meta private:
        """
        if cls == APIResource:
            raise NotImplementedError(
                "APIResource is an abstract class."
                "You should perform actions on its subclasses."
            )
        # Namespaces are separated in object names with periods (.) and in URLs
        # with forward slashes (/), so replace the former with the latter.
        base = cls.OBJECT_NAME.replace(".", "/")
        return base

    @classmethod
    def instance_url(cls, object_id: Toid):
        """
        :meta private:
        """
        if not isinstance(object_id, (str, int)):
            raise RuntimeError(
                "Could not determine which URL to request: %s instance "
                "has invalid ID: %r, %s. ID should be of type `int` or `str`"
                % (type(cls).__name__, object_id, type(id)),
                "id",
            )

        base = cls.class_url()
        return f"{base}/{object_id}/"
