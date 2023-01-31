# Quick Start

Use the DBAPI interface to query Upsolver:

```python
import cli.dbapi as upsolver
conn=upsolver.connect(
    token='',
    apiurl=''
)
cur = conn.cursor()
cur.execute('SELECT * FROM catalog.database.transformed_data LIMIT 10')
rows = cur.fetchall()
```

The DBAPI implementation in `cli.dbapi` provides methods to retrieve fewer
rows for example `Cursor.fetchone()` or `Cursor.fetchmany()`. By default
`Cursor.fetchmany()` fetches one row. Set
`cli.dbapi.Cursor.arraysize` to fetch specific number of rows with `Cursor.fetchmany()`.

After the `Cursor.execute` was invoked, descriptive attributes become available.
The `Cursor.rowcount` contains the number of rows produced by execute. 
The `Cursor.description` contains the description of columns produced by execute.

This implementation also provides `Cursor.executefile` that is not part of DBAPI, 
but can be used the same as a file can be used in `CLI`.