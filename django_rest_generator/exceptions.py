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

import json
from typing import Optional, Union, Dict, Any
from requests.exceptions import RequestException


class APIClientException(RequestException):
    @property
    def error_detail(self) -> Optional[Union[Dict, Any]]:
        content = None
        try:
            content = self.response.json()
            detail = content.get("detail", None)
            if detail:
                content = detail
        except json.JSONDecodeError:
            content = self.response.content
        except Exception:
            pass

        return content

    def __str__(self):
        err_msg = super().__str__()
        detail = self.error_detail
        return err_msg + f"\n[Details: {detail}]"
