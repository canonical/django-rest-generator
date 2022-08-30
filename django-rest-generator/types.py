from typing import List, Dict, Union
from typing_extensions import Literal, TypedDict


TRequestMethods = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]

Toid = Union[str, int]


THeaders = Dict[str, str]

class TParams(TypedDict, total=False):
    ordering: List[str]
    page: int
    page_size: int
