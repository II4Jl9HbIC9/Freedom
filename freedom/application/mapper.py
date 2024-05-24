from __future__ import annotations

__all__: typing.Sequence[str] = (
    "DataMapper",
    "MapperModelT",
    "MapperEntityT",
    "AnyDataMapper",
    "AnyDataMapperType",
)

import abc
import typing

import typing_extensions as typingext

AnyDataMapper: typingext.TypeAlias = "DataMapper[typing.Any, typing.Any]"
AnyDataMapperType: typingext.TypeAlias = typing.Type["AnyDataMapper"]

MapperEntityT = typing.TypeVar("MapperEntityT")
MapperModelT = typing.TypeVar("MapperModelT")


class DataMapper(typing.Generic[MapperEntityT, MapperModelT], abc.ABC):
    @abc.abstractmethod
    def model_to_entity(self, instance: MapperModelT) -> MapperEntityT: ...

    @abc.abstractmethod
    def entity_to_model(self, entity: MapperEntityT) -> MapperModelT: ...
