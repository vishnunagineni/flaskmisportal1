from datetime import datetime, timedelta,timezone
import json
from bson import json_util
from flask import jsonify
import jwt
import config
import pymongo
#from exchangelib import Credentials, DELEGATE, Account, Message, Mailbox,Configuration
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logging_config import logging
import openpyxl
import win32com.client as win32
import pytz
from urllib.parse import urlparse,parse_qs
# from datetime import timedelta
logger = logging.getLogger(__name__)

def connectToMWSDatabase():
    # for .30 db
    # dbUrl  = config.database_url
    # dbName = config.dbName
    # client = pymongo.MongoClient(dbUrl)
    # db = client.get_database(dbName)
    # return db

    # for azure db
    dbName = config.dbName
    client = pymongo.MongoClient(config.host, config.port, username=config.username, password=config.password)
    db = client.get_database(dbName)
    return db
    

def initDb(app):
    mws_db = connectToMWSDatabase()
    app.mws_db = mws_db

    app.jobsQueueCollection = mws_db.get_collection(config.jobsQueueCollectionName)
    app.teamCollection = mws_db.get_collection(config.teamCollectionName)
    app.fileCollection = mws_db.get_collection(config.fileCollectionName)
    app.logCollection = mws_db.get_collection(config.logCollectionName)


############  MERGED CODE ####################

def registerRoaster(app, empId, roasterDetails):
    fetchExistanceMember = app.teamCollection.find_one({'empId':empId})
    print(fetchExistanceMember)

    if fetchExistanceMember is None:
        # insertedMember = app.teamCollection.insert_one(roasterDetails)
        # return jsonify(str(insertedMember.inserted_id))
        app.teamCollection.insert_one(roasterDetails)
        return empId + " added successfully"
        
    else:
        return empId+ " already exists"



def insertSingleJob(app, jobJson):
    # for the same job we can have multiple easting northing
    jobId = jobJson["jobId"]
    easting = jobJson["easting"]
    northing = jobJson["northing"]

    fetchExistingJob = app.jobsQueueCollection.find_one({'jobId':jobId, "easting":easting, "northing":northing})

    if fetchExistingJob is None:
         app.jobsQueueCollection.insert_one(jobJson)
         return "jobId : " + jobId + " successfully added into queue"
    else:
        return "jobId : " + jobId + " is already into queue"


def insertMultipleJobs(app, mutlipleJobsJson, jobCreationDate):
    addedJobCount = 0
    notaddedJobCount = 0
    notaddedJobsList = []
    for job in mutlipleJobsJson:
        print(job)
        fetchExistingJob = app.jobsQueueCollection.find_one({'jobId':str(job["jobId"]), "easting":str(job["easting"]), "northing":str(job["northing"])})
        if fetchExistingJob is None:
            job['jobId'] = str(job['jobId'])
            job['easting'] = str(job['easting'])
            job['northing'] = str(job['northing'])
            job["jobCreationDate"] = jobCreationDate
            job["jobPlannedDate"]=str(job["jobPlannedDate"])
            job["assignTo"] = "NA"
            job["reviewedBy"] = "NA"
            job["robotStatus"] = "NA"
            job["QAStatus"] = "NA"
            job["QAAssigned"] = "NA"
            job["machine"] = "NA"
            job['isInProd'] = "no"
            job['readTimeStamp'] = ""
            app.jobsQueueCollection.insert_one(job)
            addedJobCount = addedJobCount + 1
        else:
            notaddedJobsList.append(job)
            notaddedJobCount = notaddedJobCount + 1
    print(addedJobCount)
    # totalJob = addedJobCount + notaddedJobCount
    if notaddedJobCount==0:
        return "All "+str(addedJobCount)+" jobs successfully added into queue"
    else:
        return str(notaddedJobCount)+" jobs detected as same job id, they are : "+(str(notaddedJobsList))+" , "+str(addedJobCount)+" jobs added into queue"
        # return "out of " +str(totalJob)+" jobs "+ str(addedJobCount)+" jobs added into queue"+" and not added jobs list : "+(str(notaddedJobsList))




def onPriority():
    return [["jobCreationDate",pymongo.DESCENDING], ["jobPlannedDate", pymongo.ASCENDING], ["jobType", pymongo.DESCENDING]]


########################  MIS Portal ##########################


def findAllJobDetails(app):
    jobCursor = app.jobsQueueCollection.find({}).sort(onPriority())
    # print("printing job from production")
    # if jobCursor is None:
    #     msg = {
    #         "error":"job are not available"
    #     }
    #     return msg
    resData = jsonify(json.loads(json_util.dumps(jobCursor)))
    return resData

# def findAllQAJobsForToday(app):
#     toDaysDate = datetime.today().strftime('%Y-%m-%d')
#     # add in prod option , it should not be in prod
#     jobCursor = app.jobsQueueCollection.find({'jobCreationDate':toDaysDate, 'robotStatus':'completed', 'QAStatus':{"$ne":'NA'}, 'isInProd':{"$ne":'yes'}}).sort(onPriority())
#     resData = jsonify(json.loads(json_util.dumps(jobCursor)))
#     # print(toDaysDate)
#     # print(type(toDaysDate))
#     return resData

def findAllQAJobsForToday(app):
    toDaysDate = datetime.today().strftime('%Y-%m-%d')
    # add in prod option , it should not be in prod
    jobCursor = app.jobsQueueCollection.find({'jobCreationDate':toDaysDate, 'robotStatus':'completed', 'QAStatus':{"$ne":'NA'}, 'isInProd':{"$ne":'yes'}}).sort(onPriority())
    resData = jsonify(json.loads(json_util.dumps(jobCursor)))
    # print(toDaysDate)
    # print(type(toDaysDate))
    return resData

def updateJob(app, updatedJobJson):
    queryToSearch = {'jobId':updatedJobJson['jobId'], "easting":updatedJobJson['easting'], "northing":updatedJobJson['northing']}
    updatedValue = {"$set":updatedJobJson}
    app.jobsQueueCollection.update_one(queryToSearch, updatedValue, upsert=False)

    return str(updatedJobJson['jobId']) + " has been updated"

def searchJobs(app, key, value):
    if key=="showAllJobs":
        return findAllJobDetails(app)
    
    cursorData = app.jobsQueueCollection.find({key:value}).sort(onPriority())
    resData = jsonify(json.loads(json_util.dumps(cursorData)))
    return resData


def getIndexFile(app, jobId, easting, northing):
    jobDetails = app.fileCollection.find_one({'jobId':jobId, 'easting':easting, 'northing':northing})
    print(jobDetails)
    if jobDetails is None:
        nofound = {
            'msg':"index file not found"
        }
        return nofound
    # indexFileDetails = jobDetails['index']
    # return indexFileDetails
    resData = jsonify(json.loads(json_util.dumps(jobDetails)))
    return resData

def updateIndexJson(app, jobId, easting, northing, indexJson):
    queryToSearch = {'jobId':jobId, "easting":easting, "northing":northing}
    updatedValue = {"$set":{'index':indexJson}}
    app.fileCollection.update_one(queryToSearch, updatedValue, upsert=False)
    return "QA completed for job id : "+str(jobId)



def pullJobRequest(app, username, creationDate):
    # isValidUser = app.teamCollection.find_one({'empId':username})

    isValidUser = isUserExistFromOps(app, username)

    if isValidUser is None:
        error = {
            "error" : "you are not a valid user for pulling job request"
        }
        return error
    else:
        # toDaysDate = datetime.today().strftime('%Y-%m-%d')
        jobCursor = app.jobsQueueCollection.find({"assignTo":"NA", "jobCreationDate":creationDate}, {"_id":0}).sort(onPriority())
        listOfDictForJobs = json.loads(json_util.dumps(jobCursor))
        listOfJobs = len(listOfDictForJobs)

        print(jobCursor)

        if jobCursor is None or listOfJobs <= 0:
            msg = {
                "message" : "jobs are not available for " + str(creationDate) 
            }
            return msg
        else:
            job = listOfDictForJobs[0]
            jobId = job['jobId']

            print(jobId)
            print(job)

            # update this job id with assign to username and then return

            document = app.jobsQueueCollection.find_one_and_update({'jobId':jobId}, {"$set":{"assignTo":username}}, {'_id':0}, return_document = pymongo.ReturnDocument.AFTER)
            
            return jsonify(json.loads(json_util.dumps(document)))

    # return jsonify(json.loads(json_util.dumps(jobCursor)))



def addManualModeData(app,username,machineName, jobId, easting, northing, indexJson):
    ## check jobId exist or not, if exist update the details
    queryToSearch = {'jobId':jobId, 'easting':easting, 'northing':northing}
    jobCursor = app.jobsQueueCollection.find_one(queryToSearch)

    if jobCursor is None:
        msg = {
            "error":str(jobId) + " is not exist"
        }
        return msg
    else:
        updateNodeWithVal = {'$set':{'reviewedBy':username, 'robotStatus':'completed', 'QAStatus':'pending', 'machine':machineName}}
        app.jobsQueueCollection.update_one(queryToSearch, updateNodeWithVal, upsert=False)

        ## now add the file details in filecollection

        ## if index file exist then update it or else insert it

        fileDataInFileCollection = app.fileCollection.find_one({'jobId':jobId, 'easting':easting, 'northing':northing})

        if fileDataInFileCollection is None:
            details = {
                "jobId":jobId,
                "easting":easting,
                "northing":northing,
                "totalFiles":len(indexJson),
                "index":indexJson
            }
            app.fileCollection.insert_one(details)

            msg = {
                "msg":"index file added"
            }
            return msg
        else:
            updateIndexFile = {'$set':{'totalFiles':len(indexJson), 'index':indexJson}}
            app.fileCollection.update_one(queryToSearch, updateIndexFile, upsert = False)
            
            msg = {
                "msg":"index file updated"
            }

            return msg


def jobRevert(app, jobId, easting, northing, username):
    isValidUser = isUserExistFromOps(app, username)
    
    if isValidUser is None:
        message = {
            "error" : "you are not a valid user to revert this job"
        }
        return message
    else:
        ## update the job Id
        queryToSearch = {'jobId':jobId, 'easting':easting, 'northing':northing}
        updateNodeWithVal = {'$set':{"assignTo":"NA", 'reviewedBy':'NA', 'robotStatus':'NA', 'QAStatus':'NA', 'machine':'NA'}}
        app.jobsQueueCollection.update_one(queryToSearch, updateNodeWithVal, upsert=False)

        message = {
            "success" : str(jobId) +" reverted"
        }

        return message


def getProdData(app, jobId, easting, northing, username):
    isValidUser = isUserExistFromOps(app, username)
    
    if isValidUser is None:
        message = {
            "error" : "you are not a valid user to fetch data for prod"
        }
        return message
    else:
        queryToSearch = {'jobId':jobId, 'easting':easting, 'northing':northing}
        ## finding job details
        jobDetails = app.jobsQueueCollection.find_one_and_update(queryToSearch, {"$set":{"isInProd":'yes'}},{'_id':0}, return_document = pymongo.ReturnDocument.AFTER)
        fileDetails = app.fileCollection.find_one(queryToSearch, {'_id':0})
        print(jobDetails)
        print(fileDetails)
        
        prodJson = {
            "jobDetails":jobDetails,
            "fileDetails":fileDetails
        }

        return prodJson


##############################################

def addDataInProduction(app, jobId, easting, northing, prodJsonData):

    srchQuery = {'jobId':jobId, 'easting':easting, 'northing':northing}

    jobCursor = app.jobsQueueCollection.find_one(srchQuery)
    fileCursor = app.fileCollection.find_one(srchQuery)

    if ((jobCursor is None) or (fileCursor is None)):
        app.jobsQueueCollection.insert_one(prodJsonData['jobDetails'])
        app.fileCollection.insert_one(prodJsonData['fileDetails'])
    else:
        app.jobsQueueCollection.update_one(srchQuery, {"$set":{prodJsonData['jobDetails']}}, upsert = False)
        app.fileCollection.update_one(srchQuery, {"$set":{prodJsonData['fileDetails']}}, upsert = False)

    msg = {
        "success":"added successfully"
    }
    return msg
#################################################################

################### common to android rpa and mis portal ################

def updateStatusInJob(app, jobId, easting, northhing, nodeName, updatedStatus):
    queryToSearch = {'jobId':jobId, 'easting':easting, 'northing':northhing}
    updateNodeWithVal = {'$set':{nodeName:updatedStatus}}
    app.jobsQueueCollection.update_one(queryToSearch, updateNodeWithVal, upsert=False)
    return str(jobId) + " has been updated"


def findJobByJobIdAndCoOrdinate(app, jobId, easting, northing):
    jobDetail = app.jobsQueueCollection.find_one({'jobId':jobId, 'easting':easting, 'northing':northing})

    if jobDetail is None:
        return str(jobId) + " not found"

    return jsonify(json.loads(json_util.dumps(jobDetail)))

def checkLoginCred(app, username, password):
    userDetails = app.teamCollection.find_one({"empId":username, "password":password}, {"_id":0, "password":0})
    if userDetails is None:
        return {"error": "User Not Found"}
    token = getLoginToken(app,username,password)
    data = {
        "userDetails":userDetails,
        "token":token
    }
    return data

def generateToken(data):
    exp_time=str(datetime.now(pytz.timezone('Asia/Kolkata')) + timedelta(minutes=15))
    payload={
        "userDetails":data,
        "exp_time":exp_time
    }
    # token = jwt.encode(data,config.SECRET, algorithm="HS256")
    token = jwt.encode(payload,config.SECRET, algorithm="HS256")
    token = {
        "JWTtoken":token,
        "exp_time":exp_time
    }
    return token   
        

def validateToken(token):
    try:
        data = jwt.decode(token, config.SECRET, algorithms="HS256")
        exp_time = str(data["exp_time"])
        present_time = str((datetime.now(pytz.timezone('Asia/Kolkata'))))
        if present_time<=exp_time:
            return data
        else:
            message = {
                "error":" Expired!!!"
            }
            return message
    except:
        message = {
            "error":" Invalid!!!"
        }
        return message
        

def getToken(app, email):
    # exp=datetime.utcnow()+datetime.timedelta(miunutes=1)
    # expdate = datetime.now() + timedelta(days=10)
    userDetails = app.teamCollection.find_one({"email":email},{"_id":0,"password":0})
    #print(userDetails)
    if userDetails is None:
        return {"error": "User Not Found"}

    return generateToken(userDetails)
#.......................... added for login.................................
def getLoginToken(app, username, password):
    userDetails = app.teamCollection.find_one({"empId":username, "password":password}, {"_id":0,"password":0})
    print(userDetails)
    # exp=datetime.utcnow()+datetime.timedelta(miunutes=1)
    # expdate = datetime.now() + timedelta(days=10)
    if userDetails is None:
        return {"error": "User Not Found"}

    return generateToken(userDetails)


def isUserExistFromOps(app, username):
    isValid = app.teamCollection.find_one({'email':username})
    return isValid

##########################################################################

################### RPA #########################################
def addIndexFileDetails(app, jobId, easting, northing, indexFileList):
    jobDetails = app.fileCollection.find_one({'jobId':jobId, 'easting':easting, 'northing':northing})
    if jobDetails is None:
        details = {
            "jobId":jobId,
            "easting":easting,
            "northing":northing,
            "totalFiles":len(indexFileList),
            "index":indexFileList
        }
        app.fileCollection.insert_one(details)
        return "index file uploaded for jobId : "+jobId

    return "this index file is already uploaded"


######################  end of RPA  #############################

########################## Android ##############################

def getIndexFileByJobId(app, jobId):
    jobDetails = app.jobsQueueCollection.find({'jobId':jobId})
    #print(jobDetails)
    if jobDetails is None:
        message = {
            'error':"Jobs are not available"
        }
        return message
    indexFiles = []
    for job in jobDetails:
        easting= job['easting']   
        northing= job['northing']
        indexDetail = app.fileCollection.find_one({'jobId':jobId, 'easting':easting, 'northing':northing},{'_id':0})
        if indexDetail:
            indexDetail["jobPlannedDate"]=job["jobPlannedDate"]
            indexFiles.append(indexDetail)
    if not indexFiles:
        message = {
            'error':"Index File Not Found"
        }
        return message
    resData = jsonify(indexFiles)
    return resData

def getIndexFileByPlannedDate(app, jobPlannedDate):
    jobDetails = app.jobsQueueCollection.find({"jobPlannedDate":jobPlannedDate},{"_id":0})
    if jobDetails is None:
        message = {
                "error" : "Jobs are not available for " + str(jobPlannedDate)
        }
        return message
    # indexFiles = app.jobsQueueCollection.aggregate([
    #     {
    #         '$lookup':{
    #             'from':'files',
    #             'localField':'jobId',
    #             'foreignField':'jobId',
    #             'as':'indexFiles'
    #         }
    #     },
    #     {
    #         '$match':{'jobPlannedDate':jobPlannedDate}
    #     }
    # ])
    indexFiles = []
    for job in jobDetails:
        jobId = job['jobId']
        easting= job['easting']   
        northing= job['northing']
        indexDetail = app.fileCollection.find_one({'jobId':jobId, 'easting':easting, 'northing':northing},{"_id":0})
        if indexDetail:
            indexDetail["jobPlannedDate"]=jobPlannedDate
            indexFiles.append(indexDetail)
    if not indexFiles:
        message = {
            'error':"Index File Not Found"
        }
        return message
    resData = jsonify(indexFiles)
    return resData

def getPrePostThreeDaysPlannedJobData(app):
    toDaysDate = datetime.today().strftime('%Y-%m-%d')
    nextThreeDaysDate = (datetime.today() + timedelta(days=3)).strftime('%Y-%m-%d')
    prevThreeDaysDate = (datetime.today() - timedelta(days=3)).strftime('%Y-%m-%d')
    print("start")
    print(toDaysDate)
    print(nextThreeDaysDate)
    print(prevThreeDaysDate)
    print("end")

    jobCursor = app.jobsQueueCollection.find({"jobPlannedDate":{'$gte':prevThreeDaysDate, '$lte':nextThreeDaysDate }}).sort([["jobPlannedDate", pymongo.ASCENDING], ["jobType", pymongo.DESCENDING]])

    resData = jsonify(json.loads(json_util.dumps(jobCursor)))
    return resData


def getOfflineCapablitiesData(app):
    toDaysDate = datetime.today().strftime('%Y-%m-%d')
    nextThreeDaysDate = (datetime.today() + timedelta(days=3)).strftime('%Y-%m-%d')
    prevThreeDaysDate = (datetime.today() - timedelta(days=3)).strftime('%Y-%m-%d')
    
    print("start")
    print(toDaysDate)
    print(nextThreeDaysDate)
    print(prevThreeDaysDate)
    print("end")

    # jobCursor = app.jobsQueueCollection.find({"jobPlannedDate":{'$gte':prevThreeDaysDate, '$lte':nextThreeDaysDate }}).sort([["jobPlannedDate", pymongo.ASCENDING], ["jobType", pymongo.DESCENDING]])

    # jobCursor = app.jobsQueueCollection.aggregate({'$lookup':{'from':app.fileCollection, 'localField':'jobId', 'foreignField': 'jobId', 'as':"indexDetails"}})
    jobCursor = app.jobsQueueCollection.aggregate([
        {'$lookup' : {'from': 'files','localField': 'jobId','foreignField': 'jobId','as': 'index'}},
        {'$unwind': '$index'},
        {'$match':{'jobPlannedDate':{'$gte':prevThreeDaysDate, '$lte':nextThreeDaysDate}}},
        {'$sort':{'jobPlannedDate':pymongo.ASCENDING, 'jobType':pymongo.DESCENDING}}
        ])

    resData = jsonify(json.loads(json_util.dumps(jobCursor)))
    return resData



def getWorkBookSheet(filePath, sheet, readMode):
    f = open(filePath, readMode)
    wb = openpyxl.load_workbook(f)
    excelSheet = wb[sheet]
    return excelSheet

def sendMail(app,username):
    userDetails = isUserExistFromOps(app, username)
    if userDetails is None:
        notFoundMessage = {
            "message" : "Not a Valid User"
        }
        return notFoundMessage   
    else:
        token=getToken(app, username)
        print(token)
        sender = config.senderMail
        password = config.outlookPassword
        # password = config.gmailPassword
        print(password)
        baseurl = config.resetPasswordUrl
        
        url = baseurl +"/"+token["JWTtoken"]
        # url=baseurl +"?token="+token ["JWTtoken"]
        print(url)
        subject = "Reset Your Password"
        messageBody = 'Hi ' + userDetails['name'] +',' +'\n\n'+ 'You recently requested to reset the password for your account. Click the URL below to proceed.\n'+url+'\nIf you did not request a password reset, please ignore this email or reply to let us know. This password reset link is only valid for the next 15 minutes.\n\n\n\nRegards,\nVishnu.'
        receiverMail = userDetails['email']
        response, mailStatus = dropMailOutLook(sender,password,receiverMail, subject, messageBody)
        # dropMailOutLook(receiverMail, subject, messageBody)
        if mailStatus:
            message = {
                "message" : response,
                "url" : messageBody
            }
            return message
        else:
            message = {
                "message": response
            }
            return message

def dropMailOutLook(sender,password,receiver, mailSubject, mailBody):
    '''<------------------------------ Using SMTP Package ---------------------------------->'''
    host = 'smtp.office365.com'
    # host = 'smtp.gmail.com'
    port = 587
    server = smtplib.SMTP(host,port)
    check = server.ehlo()
    if check[0]==250:
        print("Successfully connected to Smtp server!!!!")
    else:
        print("Unable to connect to Smtp server!!!!!")
        msge="Unable to connect to Smtp server!!!!!"
        return msge, 0
    #start TLS encryption
    server.starttls()
    #logging into the account
    try:
        server.login(sender,password)
        print("Login Successful!!!")
        print('')
    except smtplib.SMTPAuthenticationError as e:
        print("Exception: ",e)
        print('')
        return "Authentication Unsuccessfull, the User Credentials were incorrect, Please try again!!!",0
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = mailSubject
    msg.attach(MIMEText(mailBody,'plain'))
    print(msg)
    text = msg.as_string()
    out = server.send_message(msg)
    print(out)
    if not out:
        msge = "Mail Sent Successfully!!!"
        del msg
        server.quit()
        return msge,1
    else:
        msge = 'Unable to Send, Please try again!!!!!'
        del msg
        server.quit()
        return msge,0
    

    # '''<--------------------------- Using Exchange Lib for outlook --------------------------->'''
    # credentials = Credentials(username=sender,password=password)
    # print(credentials)
    # config = Configuration(server='outlook.office365.com',credentials=credentials)
    # my_acc = Account(
    #     primary_smtp_address=sender,
    #     config=config,
    #     autodiscover=False,
    #     access_type=DELEGATE
    # )
    # m = Message(
    #     account=my_acc,
    #     subject = mailSubject,
    #     body = mailBody,
    #     to_recipients = [
    #         Mailbox(email_address=receiver)
    #     ]
    # )
    # m.send_and_save()
    """<---------------------------------- Using Outlook Application ------------------------------------------->"""
    # outlook = win32.Dispatch('outlook.application')
    # mail = outlook.CreateItem(0)
    # mail.To = receiver
    # mail.Subject = mailSubject
    # #RECEVIED URL
    # mail.Body = mailBody
    # mail.Send()

def resetAndroidPassword(app,email,confirmpassword):
    #token=fetchTokenForPasswordReset(url)
    #a.
    # payload=validateToken(token)
    # print(payload)
    #b. got user record
    #userDetails = isUserExistFromOps(app, username)
    # if payload is None:
    #     return " user not exist, invalid token"
    # #c.fectch emailid
    # email = payload['email']
    #query to search
    queryToSearch = {'email':email}
    print("email is {}".format(queryToSearch))
    #updated password
    updatedPassword = {'$set':{"password":confirmpassword}}
    print("updatedPassword is {}".format(updatedPassword))
    #f.upadate password
    if app.teamCollection.update_one(queryToSearch, updatedPassword, upsert=False):
        return "Password Updated Successfully"
    else:
        return None 


# FETCH TOKEN FROM URL/FETCH PASSWORD FROM TOKEN
def fetchTokenForPasswordReset(url): 
    #fetchTokenForPasswordReset(app,url,newpassword,confirmpassword): 
    url1=url
    #parse_result = urlparse(url1)
    parse_result = urlparse.urlparse(url1)
        #S2 FETCH TOKEN FROM URL
    captured_token = urlparse.parse_qs( parse_result.query)['token'][0]
    print(parse_result)
    print(captured_token)
       #FROM TOKEN WILL FETCH USERNAME AND PASSWORD
        #S2 PASS TOKEN THROUGH resetAndroidPassword(token) 
       #resetAndroidPassword(app,captured_token)
    return captured_token


############################ end of Android #####################