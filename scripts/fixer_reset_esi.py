# Author: Rustam Gubaydullin (@second_fry)
# License: MIT (https://opensource.org/licenses/MIT)

from pymongo import MongoClient

from statsconfig import StatsConfig

DBClient = MongoClient(StatsConfig.MONGODB_URL)
DB = DBClient.WDS_statistics_v3

kms = DB.killmails.find()
counter = 0
for km in kms:
  counter += 1
  if counter % 1000 == 0:
    print('Processed {}'.format(counter))

  esi = DB.esi_killmails.find_one({'_id': km['_id']})
  if esi:
    continue
  
  print(esi)
  raise

  DB.killmails.update_one({'_id': km['_id']}, {'$set': {'status.esi': False}})
