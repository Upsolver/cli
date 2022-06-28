# v0.1.7
## Improvements
- Minor bug fixes
- Changed `this` thing

# v0.1.6
- csv output format now flattens complex objects (object 'a' with nested objected 'b' will show up as "a.b" column).
- csv output columns are now sorted alphabetically.

# v0.1.5
- removed `export` option for `clusters` sub-command.

- fixed a bug related to CSV output formatting.

- `--version` now shows correct version

# v0.1.4
- `ls` sub-commands now return "raw" responses from the API. Prior to this the responses were converted to simplified objects, which missed a lot of info. These simplified objects are still used in the `stats` screens but need some work to show useful info.

- `execute` sub-command now has a timeout flag `--timeout` or `-t`: it controls how much time the CLI should wait for results (of pending responses) to become ready. This timeout settings is *per* statement.

- Added `InvalidOptionErr` that will now be thrown when users pass invalid option values (e.g. badly formatted time value for the timeout setting).


# v0.1.3
## Improvements
- Improved error messages.

- Passing the `--debug` flag to the CLI will now print the full stacktrace in case of an error (previously only log statements were shown).

- Implemented `export` sub-commands for `catalogs` and `jobs` (note: `jobs export` requires a job ID, and will not work with a job's name).

### `execute` sub command

- File paths are now supported. Now you have two options for executing script files:

```
$ upsolver execute commands.sql
$ cat commands.sql | upsolver execute -
```

- Execution of multiple statements now outputs "markers" that separate results of different queries. With this you can use other tools to parse the results and attribute them to specific queries. Example output:

```
$ upsolver execute "SELECT COUNT(*) FROM Athena.prod.files; SELECT * FROM Athena.prod.files limit 1;"
{
  "marker": "execution_start",
  "query": "SELECT COUNT(*) FROM Athena.prod.files;"
}
{
  "_col0": "15"
}
{
  "marker": "execution_start",
  "query": "SELECT * FROM Athena.prod.files limit 2;"
}
{
  <json doc>
}
{
  <json doc>
}
```

- Support for a "silent" flag (`-s` or `--ignore-erros`) which ignores errors. If this flag is passed to `execute` it will not stop execution on failed queries. This is useful for scripts where you have queries that are expected to fail (e.g. creating a table that already exists, or deleting a job that doesn't exist). Example:

Without silent flag:

```
$ upsolver execute "DROP TABLE Athena.prod.doesntexist; SELECT * from Athena.prod.files limit 1;"
{
  "marker": "execution_start",
  "query": "DROP TABLE Athena.prod.doesntexist;"
}
API Error [status_code=400, request_id=6b400c82-3427-417c-9b0a-695d9ad4c101]: Table Athena.prod.doesntexist was not found
```

With silent flag:
```
$ upsolver execute -s "DROP TABLE Athena.prod.doesntexist; SELECT * from Athena.prod.files limit 1;"
{
  "marker": "execution_start",
  "query": "DROP TABLE Athena.prod.doesntexist;"
}
{
  "query": "DROP TABLE Athena.prod.doesntexist;",
  "error": "API Error [status_code=400, request_id=c3c044ed-fb1f-4ce3-a619-25e0fa9fd6da]: Table Athena.prod.doesntexist was not found"
}
{
  "marker": "execution_start",
  "query": "SELECT * from Athena.prod.files limit 1;"
}
{
  <json doc>
}
```

## Fixes
- Fixed `execute` sub-command to handle non `SELECT` statements correctly.
- Fixed a bug where the execution of a query would buffer the entire result before outputting it; now the CLI outputs whatever results are available immediately.
