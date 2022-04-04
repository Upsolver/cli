from pathlib import Path

from requests_mock import Mocker as RequestsMocker

from cli.commands.context import CliContext
from cli.config import ConfigurationManager
from tests.mock_upsolver_rest_api import MockUpsolverRestApi


def test_split_simple(requests_mock: RequestsMocker, tmp_path: Path) -> None:
    MockUpsolverRestApi(requests_mock)
    lexer = CliContext(ConfigurationManager(tmp_path / 'conf')).query_lexer()
    statements = lexer.split('SELECT * FROM something')
    assert len(statements) == 1
    assert statements[0] == 'SELECT * FROM something'


def test_split(requests_mock: RequestsMocker, tmp_path: Path) -> None:
    MockUpsolverRestApi(requests_mock)
    lexer = CliContext(ConfigurationManager(tmp_path / 'conf')).query_lexer()
    statements = lexer.split('''
CREATE MYSQL CONNECTION mysql_connection
    CONNECTION_STRING = 'jdbc:mysql://demo.c4q3plwekwnv.us-east-1.rds.amazonaws.com:3306/demo'
    USER_NAME = 'your username'
    PASSWORD = 'your password'
    MAX_CONCURRENT_CONNECTIONS = 10;
-- this is a comment    ;

-- Copy from S3 into the staging table
CREATE JOB "extract data from s3"
    COMPUTE_CLUSTER = 'cluster name'
    DATE_PATTERN = 'yyyy/MM/dd'
    INITIAL_LOAD_PREFIX = 'file prefix' -- (Optional) Only files matching this prefix will be loaded when the job runs.
    INITIAL_LOAD_PATTERN = 'regex' -- (Optional) Only files matching this regex pattern will be loaded when the job runs.
    CONTENT_TYPE = JSON -- (Optional)
    STARTING_FROM = BEGINNING -- Optional defult is BEGINING other values NEW, or timestamp
    COMPRESSION = AUTO -- the compression used for the input. Supported options GZIP, KCL, LZO, NONE, SNAPPY and SNAPPY_UNFRAMED. default is AUTO
    MAX_DELAY = 1 DAY -- The amount of time to subtract from now when listing for new files. Files that show up in old folders further past than the max_delay will not be discovered when using a date pattern. Setting this to a very high value may cause excessive lists.
    AS COPY FROM S3 orders BUCKET = 'your bucket name' PREFIX = 'path/to/your/data/'
    INTO athena.default.extracted_data_stg;

;
SELECT * FROM tablfoo;

    ''')

    assert len(statements) == 3
    assert statements[0] == '''CREATE MYSQL CONNECTION mysql_connection
    CONNECTION_STRING = \'jdbc:mysql://demo.c4q3plwekwnv.us-east-1.rds.amazonaws.com:3306/demo\'
    USER_NAME = \'your username\'
    PASSWORD = \'your password\'
    MAX_CONCURRENT_CONNECTIONS = 10;'''

    assert statements[1] == '''-- this is a comment    ;

-- Copy from S3 into the staging table
CREATE JOB "extract data from s3"
    COMPUTE_CLUSTER = 'cluster name'
    DATE_PATTERN = 'yyyy/MM/dd'
    INITIAL_LOAD_PREFIX = 'file prefix' -- (Optional) Only files matching this prefix will be loaded when the job runs.
    INITIAL_LOAD_PATTERN = 'regex' -- (Optional) Only files matching this regex pattern will be loaded when the job runs.
    CONTENT_TYPE = JSON -- (Optional)
    STARTING_FROM = BEGINNING -- Optional defult is BEGINING other values NEW, or timestamp
    COMPRESSION = AUTO -- the compression used for the input. Supported options GZIP, KCL, LZO, NONE, SNAPPY and SNAPPY_UNFRAMED. default is AUTO
    MAX_DELAY = 1 DAY -- The amount of time to subtract from now when listing for new files. Files that show up in old folders further past than the max_delay will not be discovered when using a date pattern. Setting this to a very high value may cause excessive lists.
    AS COPY FROM S3 orders BUCKET = 'your bucket name' PREFIX = 'path/to/your/data/'
    INTO athena.default.extracted_data_stg;'''

    assert statements[2] == 'SELECT * FROM tablfoo;'
