from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Generic, Optional, TypeVar

from dataclasses_json import config, dataclass_json

from cli.upsolver import entities
from cli.upsolver.entities import ApiEntity, Catalog, Cluster, Job, Worksheet

TApiEntity = TypeVar('TApiEntity', bound='ApiEntity')


class RawEntity(Generic[TApiEntity], ABC):
    """
     "Raw Entities" are actual entities we get in response from Upsolver's API. They are usually
      more complex than the entities used in CLI code.

      TApiEntity represents the "higher level" api type that the raw object is mapped to.
    """
    @abstractmethod
    def to_api_entity(self) -> TApiEntity:
        pass


@dataclass_json
@dataclass
class DisplayData:
    created_by: str = field(metadata=config(field_name='createdBy'))
    creation_time: str = field(metadata=config(field_name='creationTime'))
    desc: str = field(metadata=config(field_name='description'))
    name: str
    modified_by: Optional[str] = field(metadata=config(field_name='modifiedBy'), default=None)
    modified_time: Optional[str] = field(metadata=config(field_name='modifiedTime'), default=None)


@dataclass_json
@dataclass
class Connection:
    kind: str = field(metadata=config(field_name='clazz'))
    display_data: DisplayData = field(metadata=config(field_name='displayData'))
    display_name: Optional[str] = field(metadata=config(field_name='displayValue'), default=None)


@dataclass_json
@dataclass
class ConnectionInfo(RawEntity[Catalog]):
    extra_org_ids: list[str] = field(metadata=config(field_name='extraOrganizationIds'))
    workspaces: list[str]
    connection: Connection
    org_id: str = field(metadata=config(field_name='organizationId'))
    id: str

    def to_api_entity(self) -> Catalog:
        return Catalog(
            id=self.id,
            name=self.connection.display_data.name,
            created_by=self.connection.display_data.created_by,
            kind=self.connection.kind,
            org_id=self.org_id
        )


@dataclass_json
@dataclass
class CustomerEnvironment:
    id: str
    org_id: str = field(metadata=config(field_name='organizationId'))
    display_data: DisplayData = field(metadata=config(field_name='displayData'))
    running: bool


@dataclass_json
@dataclass
class EnvironmentDashboardResponse(RawEntity[Cluster]):
    env: CustomerEnvironment = field(metadata=config(field_name='environment'))

    def to_api_entity(self) -> Cluster:
        return Cluster(
            name=self.env.display_data.name,
            id=self.env.id,
            running=self.env.running
        )


@dataclass_json
@dataclass
class TableColumn:
    name: str


@dataclass_json
@dataclass
class Compression:
    name: str = field(metadata=config(field_name='displayName'))


@dataclass_json
@dataclass
class Table(RawEntity[entities.Table]):
    id: str
    org_id: str = field(metadata=config(field_name='organizationId'))
    display_data: DisplayData = field(metadata=config(field_name='displayData'))
    running: bool = field(metadata=config(field_name='isRunning'))
    partitions_columns: list[TableColumn] = field(metadata=config(field_name='partitionColumns'))
    compression: Compression

    def to_api_entity(self) -> entities.Table:
        return entities.Table(
            id=self.id,
            name=self.display_data.name,
            compression=self.compression.name,
            is_running=self.running,
        )


@dataclass_json
@dataclass
class JobInfo(RawEntity[Job]):
    name: str
    description: str
    status: str

    def to_api_entity(self) -> Job:
        return Job(
            id='',  # JobInfo returned from API has no id...
            name=self.name,
            status=self.status
        )


@dataclass_json
@dataclass
class WorksheetUri:
    id: str


@dataclass_json
@dataclass
class WorksheetView(RawEntity[Worksheet]):
    uri: str
    title: str = field(metadata=config(field_name='name'))
    body: Optional[str] = None

    def to_api_entity(self) -> Worksheet:
        return Worksheet(
            id=self.uri,  # JobInfo returned from API has no id...
            title=self.title,
            body=self.body
        )
