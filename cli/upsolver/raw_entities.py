from dataclasses import dataclass, field
from typing import Optional

from dataclasses_json import config, dataclass_json

# "Raw Entities" are actual entities we get in response from Upsolver's API. They are usually
# more complex than the entities used in CLI code. Some of the raw entities can be converted
# to the corresponding CLI entities (e.g. ConnectionInfo is convertible to Catalog).
from cli.upsolver import entities
from cli.upsolver.entities import Catalog, Cluster, Job


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
class ConnectionInfo:
    extra_org_ids: list[str] = field(metadata=config(field_name='extraOrganizationIds'))
    workspaces: list[str]
    connection: Connection
    org_id: str = field(metadata=config(field_name='organizationId'))
    id: str

    def to_catalog(self) -> Catalog:
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
class EnvironmentDashboardResponse:
    env: CustomerEnvironment = field(metadata=config(field_name='environment'))

    def to_cluster(self) -> Cluster:
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
class Table:
    id: str
    org_id: str = field(metadata=config(field_name='organizationId'))
    display_data: DisplayData = field(metadata=config(field_name='displayData'))
    running: bool = field(metadata=config(field_name='isRunning'))
    partitions_columns: list[TableColumn] = field(metadata=config(field_name='partitionColumns'))
    compression: Compression

    def to_table(self) -> entities.Table:
        return entities.Table(
            id=self.id,
            name=self.display_data.name,
            compression=self.compression.name,
            is_running=self.running,
        )


@dataclass_json
@dataclass
class JobInfo:
    name: str
    description: str
    status: str

    def to_job(self) -> Job:
        return Job(
            name=self.name,
            status=self.status
        )
