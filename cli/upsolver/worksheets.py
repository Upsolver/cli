import builtins
from abc import ABC, abstractmethod
from typing import Any

from cli.upsolver.entities import Worksheet
from cli.upsolver.raw_entities import WorksheetView
from cli.upsolver.requester import Requester
from cli.utils import from_dict

WorksheetId = str


class RawWorksheetsApi(ABC):
    @abstractmethod
    def list(self) -> list[dict[str, Any]]:
        pass

    def list_worksheets_info(self) -> builtins.list[WorksheetView]:
        return [from_dict(WorksheetView, ji) for ji in self.list()]


class RawWorksheetsApiProvider(ABC):
    @property
    @abstractmethod
    def raw(self) -> RawWorksheetsApi:
        pass


class WorksheetsApi(RawWorksheetsApiProvider, ABC):
    def list(self) -> list[Worksheet]:
        return [worksheet.to_api_entity() for worksheet in self.raw.list_worksheets_info()]


class WorksheetsApiProvider(ABC):
    @property
    @abstractmethod
    def worksheets(self) -> WorksheetsApi:
        pass


class RawRestWorksheetsApi(RawWorksheetsApi):
    def __init__(self, requester: Requester):
        self.requester = requester

    def list(self) -> list[dict[str, Any]]:
        return self.requester.get_list('worksheets/documents', list_field_name='worksheets')


class RestWorksheetsApi(WorksheetsApi, WorksheetsApiProvider):
    def __init__(self, requester: Requester):
        self.requester = requester
        self.raw_api = RawRestWorksheetsApi(self.requester)

    @property
    def worksheets(self) -> WorksheetsApi:
        return self

    @property
    def raw(self) -> RawWorksheetsApi:
        return self.raw_api
