from abc import ABC

from cli.upsolver.auth import AuthApi
from cli.upsolver.query import QueryApi

"""
General pattern you'll see here:

RawXApi: Defines interface methods that return raw responses (json) from the API.
         The only parsing / handling performed is extraction of the result from the
         response body.

         Not all API methods are exposed in raw form, only those that are needed.
         For example, when listing objects (e.g. catalogs) we want to list them in raw
         form (i.e. print them out when the user issues 'upsolver catalogs ls' command).
         On the other hand, we have no use for raw responses of "export" api calls and
         so you won't see them in RawXApis.

RawXApiProvider: Declares a `raw` property that returns the raw api implmentation.
                 this is used to access the raw / lower level API:

                 catalogs_api      # CatalogsApi
                 catalogs_api.raw  # RawCatalogsApi

XApi: Defines "higher level" API for resource X. The returned objects are fully typified.
      Also implements RawXApiProvider, which enables us to write:

      catalogs_api.raw.get()  # returns raw json dictionaries representing catalogs
      catalogs.get()          # returns typified objects representing catalogs

XApiProvider: provides XApi using a certain name. Allows for code of the form:

              upsolver_api().catalogs  # .catalogs returns CatalogsApi,
                                       # upsolver_api() implements CatalogsApiProvider

RawRestXApi: Implements RawXApi.

RestXApi: Implements both XApi and XApiProvider (as a provider of the API it will return itself).
          Internally it will build RawXApi as it also implements RawXApiProvider (via XApi).

 ----------

In summary, UpsolverApi implements some Api interfaces directly
  for example auth:
    upsolver_api().auth(...)

but, most of the resources are accessed by named properties:

api: UpsolverApi = build()  # UpsolverApi implements ClustersApiProvider

api.clusters      # returns ClustersApi (which implements RawClustersApiProvider)
api.clusters.raw  # returns RawClustersApi

and this pattern recurs for all types of entities: clusters, catalogs, jobs, tables (& others in
the future)
"""


class UpsolverApi(
    AuthApi,
    QueryApi,
    ABC
):
    pass
