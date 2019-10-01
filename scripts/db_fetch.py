# Author: Rustam Gubaydullin (@second_fry)
# License: MIT (https://opensource.org/licenses/MIT)

from scripts.log import log


class DBFetcher(object):
  LOG_LEVEL = 1

  @staticmethod
  def factory(type):
    """
    Provides DB creator

    :param type Selects type of DB creator
    """
    if type == "zkillboard-mongo":
      from scripts.DBFetcherZkillboardMongo.fetcher import DBFetcherZkillboardMongo
      log(DBFetcher.LOG_LEVEL, 'Creating zkillboard fetcher with MongoDB on our side')
      return DBFetcherZkillboardMongo()

    if type == "esi-mongo":
      from scripts.DBFetcherESIMongo.fetcher import DBFetcherESIMongo
      log(DBFetcher.LOG_LEVEL, 'Creating ESI fetcher with MongoDB on our side')
      return DBFetcherESIMongo()

    raise AssertionError('Source {} is not defined'.format(type))
