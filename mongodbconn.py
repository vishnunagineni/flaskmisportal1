import config
import pymongo

def connectMWSDatabase():
    dbName = config.dbName
    client = pymongo.MongoClient(config.host, config.port, username=config.username, password=config.password)
    db = client.get_database(dbName)
    col = db.get_collection(config.jobsQueueCollectionName)
    users = col.find()
    for user in users:
        print(user['jobId'])
    #query={'empId':'SB67470'}
    #updatedPassword= {"$set":{"password":1237}}
    #col.update_one(query,updatedPassword,upsert=False)
    #print(res)
    #col.insert_one({'name':'Bajirang Bhairu Namade','empId':'BN67926','email':'b.namade@zensar.com','password':'1234','machineName':'Bajirang','role':'admin'})
    query = {'jobId':'95759021'}
    col.delete_one(query)
connectMWSDatabase()