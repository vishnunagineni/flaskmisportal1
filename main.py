from flask import Flask, app, json, request, render_template,jsonify
from logging_config import logging
import util
import packService
import os
from functools import wraps
# from werkzeug.utils import safe_join as _safe_join
import config
from flask import safe_join as _safe_join
import requests
safe_join = lambda r,*paths: os.path.normpath(_safe_join(r,*[p.replace(os.path.sep,"/") for p in paths]))


logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.before_request
def initializeMWSDB():
    util.initDb(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

@app.route('/', methods=['GET'])
def hello():
    return "MWS Production End Points"

######################  MIS Portal  ##########################

################ MERGE API ##############
@app.route('/mis/addRoaster', methods=['POST'])    
def addRoaster():
    roasterName = request.form.get('roasterName')
    empId = request.form.get('empId')
    email = request.form.get('email')
    machineId = request.form.get('machineId')
    password = request.form.get('password')
    role = request.form.get('role')


    roasterDetails = packService.roasterDetails(roasterName, empId, email, machineId, password, role)
    insertedMember = util.registerRoaster(app, empId, roasterDetails)
    
    return insertedMember


@app.route('/mis/mapSingleJob', methods=['POST'])
def mapSingleJob():
    singleJobDetails = request.form.get('singleJobDetails')
    jobJson = json.loads(singleJobDetails)
    addedMsg = util.insertSingleJob(app, jobJson)
    print(jobJson)
    
    return addedMsg

@app.route('/mis/mapJobFromExcel', methods=['POST'])
def mapJobsFromExcel():
    jobCreationDate = request.form.get('jobCreationDate')
    multipleJobDetails = request.form.get('multipleJobDetails')
    print(multipleJobDetails)
    multJobJson = json.loads(multipleJobDetails)
    addedMsg = util.insertMultipleJobs(app, multJobJson, jobCreationDate)
    return addedMsg


@app.route('/mis/getAllJobDetailsForMIS', methods=['GET'])
def getAllJobDetailsForMIS():
    jobDetailsList = util.findAllJobDetails(app)
    return jobDetailsList


@app.route('/mis/updateJob', methods=['PUT'])
def updateJob():
    updatedJobDetails = request.form.get('updatedJobDetails')
    updatedJobJson = json.loads(updatedJobDetails)
    updatedMsg = util.updateJob(app, updatedJobJson)
    return updatedMsg


@app.route('/mis/search', methods = ['GET'])
def searchJobsForMIS():
    key =request.args.get('key')
    value =request.args.get('value')

    searchedJobs = util.searchJobs(app, key, value)
    return searchedJobs


@app.route('/mis/getAllQAJobsForToday', methods=['GET'])
def getAllQAJobsForToday():
    todaysQAJobsList = util.findAllQAJobsForToday(app)
    return todaysQAJobsList


@app.route('/mis/getIndexFile', methods = ['GET'])
def getIndexFileForMIS():
    jobId = request.args.get('jobId')
    easting = request.args.get('easting')
    northing = request.args.get('northing')
    indexJson = util.getIndexFile(app, jobId, easting, northing)
    return indexJson


@app.route('/mis/updateIndexFile', methods = ['PUT'])
def updateIndexFile():
    jobId = request.form.get('jobId')
    easting = request.form.get('easting')
    northing = request.form.get('northing')
    print(jobId, easting, northing)
    indexJson = json.loads(request.form.get('updatedIndexJson'))

    updatedMsg = util.updateIndexJson(app, jobId, easting, northing, indexJson)
    # print(indexJson)

    return updatedMsg



@app.route('/mis/updateNodeInJob', methods = ['PUT'])
def updateNodeInJob():
    jobId = request.form.get('jobId')
    easting = request.form.get('easting')
    northing = request.form.get('northing')
    nodeName = request.form.get('nodeName')
    updatedStatus = request.form.get('statusMessage')
    updatedMsg = util.updateStatusInJob(app, jobId, easting, northing, nodeName, updatedStatus)
    return updatedMsg

@app.route('/mis/getJobDetailByJobIdAndCoOrdinate', methods=['GET'])
def getJobDetailByJobIdAndCoOrdinate():
    jobId = request.args.get('jobId')
    easting = request.args.get('easting')
    northing = request.args.get('northing')

    jobdetail = util.findJobByJobIdAndCoOrdinate(app, jobId, easting, northing)
    return jobdetail

def token_required(f):
    @wraps(f)
    def protecteddecorator(*args,**kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'error':'Token is Missing!!'})
        try:
            data,status = util.validateToken(token)
            if not status:
                return data
        except:
            return jsonify({'error':'Token is Invalid!!'})
        return f(*args,**kwargs)
    
    return protecteddecorator



@app.route('/mis/login', methods = ['POST'])
def loginToMis():
    username = request.form.get('username')
    password = request.form.get('password')
    #data,status = util.validateToken()
    loginRes = util.checkLoginCred(app, username, password)
    print(loginRes)
    return loginRes



@app.route('/mis/getLoginToken', methods = ['POST'])
def getLoginToken():
    username = request.form.get('username')
    password = request.form.get('password')
    if username is None or password is None:
        error = {
            "response" : "Invalid Credentials!!!"
        }
        return error
    loginRes = util.getLoginToken(app, username,password)
    return loginRes

@app.route('/mis/validateLoginToken', methods = ['GET'])
def validateLoginToken():
    token = request.args.get('token')
    data = util.validateToken(token)
    return data
    

@app.route('/mis/getTeamDetails', methods = ['GET'])
def getTeamDetails():
    # if you are the valid user then only you can get team details
    pass

@app.route('/mis/pullJobRequestForCreationDate', methods=['GET'])
def pullJobRequestFromMISForCreationDate():
    username = request.args.get('username')
    creationDate = request.args.get('creationDate')
    pulledJobDetail = util.pullJobRequest(app, username, creationDate)
    return pulledJobDetail


@app.route('/mis/manaulMode', methods = ['POST'])
def manualMode():
    username = request.form.get('username')
    machineName = request.form.get('machine')
    jobId = request.form.get('jobId')
    easting = request.form.get('easting')
    northing = request.form.get('northing')
    indexFileJson = json.loads(request.form.get('indexFile'))

    # print(indexFileJson)
    manualModeMsg = util.addManualModeData(app,username,machineName, jobId, easting, northing, indexFileJson)
    return manualModeMsg


@app.route('/mis/revertJob', methods = ['POST'])
def revertJob():
    jobId = request.form.get('jobId')
    easting = request.form.get('easting')
    northing = request.form.get('northing')
    username = request.form.get('username')
    msg = util.jobRevert(app, jobId,easting, northing, username)
    return msg


@app.route('/mis/getProdData', methods=['POST'])
def getProdDataForMIS():
    jobId = request.form.get('jobId')
    easting = request.form.get('easting')
    northing = request.form.get('northing')
    username = request.form.get('username')
    dataOrMsg = util.getProdData(app, jobId, easting, northing, username)
    return dataOrMsg


@app.route('/rpa/uploadIndexFileData', methods=['POST'])
def uploadIndexFileData():
    jobCreationDate = request.form.get('jobCreationDate')
    jobId = request.form.get('jobId')
    easting = request.form.get('easting')
    northing = request.form.get('northing')
    indexFileList = packService.indexFileToJson(jobCreationDate, jobId, easting, northing)
    print(indexFileList)
    addedMsg = util.addIndexFileDetails(app, jobId, easting, northing, indexFileList)
    return addedMsg


##########################################

@app.route('/mis/moveToProd', methods = ['POST'])
def moveDataInProd():
    jobId = request.form.get('jobId')
    easting = request.form.get('easting')
    northing = request.form.get('northing')
    prodJson = json.loads(request.form.get('prodData'))
    msg = util.addDataInProduction(app, jobId, easting, northing, prodJson)
    # print(prodJson['jobDetails'])
    # print(prodJson['fileDetails'])
    return msg
##########################################################################

################### RPA ########################################


##############################  end of  RPA ############################################

############################### Android ###################################################

@app.route('/android/search/jobId', methods = ['GET'])
def searchJobsForMobileAppJobId():
    jobId = request.args.get('jobId')
    jobDetails = util.getIndexFileByJobId(app,jobId)
    return jobDetails

@app.route('/android/search/jobPlannedDate', methods = ['GET'])
def searchJobsForMobileAppPlannedDate():
    jobPlannedDate = request.args.get('jobPlannedDate')
    jobDetails = util.getIndexFileByPlannedDate(app,jobPlannedDate)
    return jobDetails

@app.route('/android/getPrePostThreeDaysPlannedJobData', methods=['GET'])
def getPrePostThreeDaysPlannedJobData():
    jobData = util.getPrePostThreeDaysPlannedJobData(app)
    return jobData

@app.route('/android/updateNode', methods = ['PUT'])
def updateNode():
    jobId = request.form.get('jobId')
    easting = request.form.get('easting')
    northing = request.form.get('northing')
    nodeName = request.form.get('nodeName')
    updatedStatus = request.form.get('statusMessage')
    updatedMsg = util.updateStatusInJob(app, jobId, easting, northing, nodeName, updatedStatus)
    return updatedMsg

@app.route('/android/getAllJobDetails', methods=['GET'])
def getAllJobDetailsForMobileApp():
    jobDetailsList = util.findAllJobDetails(app)
    return jobDetailsList

@app.route('/android/updateJob', methods=['PUT'])
def updateJobForMobileApp():
    updatedJobDetails = request.form.get('updatedJobDetails')
    updatedJobJson = json.loads(updatedJobDetails)
    updatedMsg = util.updateJob(app, updatedJobJson)
    return updatedMsg

@app.route('/android/search', methods = ['GET'])
def searchJobsForMobileApp():
    key =request.args.get('key')
    value =request.args.get('value')

    searchedJobs = util.searchJobs(app, key, value)
    return searchedJobs

@app.route('/android/getIndexFile', methods = ['GET'])
def getIndexFileForMobileApp():
    jobId = request.args.get('jobId')
    easting = request.args.get('easting')
    northing = request.args.get('northing')
    indexJson = util.getIndexFile(app, jobId, easting, northing)
    return indexJson

@app.route('/android/updateIndexFile', methods = ['PUT'])
def updateIndexFileForMobileApp():
    jobId = request.form.get('jobId')
    easting = request.form.get('easting')
    northing = request.form.get('northing')
    print(jobId, easting, northing)
    indexJson = json.loads(request.form.get('updatedIndexJson'))

    updatedMsg = util.updateIndexJson(app, jobId, easting, northing, indexJson)
    # print(indexJson)

    return updatedMsg

@app.route('/android/getJobDetailByJobIdAndCoOrdinate', methods=['GET'])
def getJobDetailByJobIdAndCoOrdinateForMobileApp():
    jobId = request.args.get('jobId')
    easting = request.args.get('easting')
    northing = request.args.get('northing')

    jobdetail = util.findJobByJobIdAndCoOrdinate(app, jobId, easting, northing)
    return jobdetail

@app.route('/android/getDataForOfflineCapablities', methods=['GET'])
def getDataForOffline():
    jobData = util.getOfflineCapablitiesData(app)
    return jobData

#..............................FOR RESET PASSWORD...............................

@app.route('/android/resetPassword',methods=['POST'])
def forgetPassword():
    email=request.form.get('email')
    if not email:
        error = {
            "error": "Invalid Mail!!!!"
        }
        return error
    print(email)
    message=util.sendMail(app,email)
    return message


@app.route('/mobile/updatePassword',methods=['POST','GET'])
#@token_required
def updatePassword():
    token=request.args.get('token')
    print(token)
    confirmPassword = request.form.get('confirmPassword')
    payload=util.validateToken(token)
    email= payload['userDetails']['email']
    res = util.resetAndroidPassword(app,email,confirmPassword) 
    if res is None:
        response = {"error":"Password Update Failed!!"}
        return response
    else:
        response = { "message": res}
        return response
           
@app.route('/mobile/tokenValidation',methods=['GET','POST'])
def tokenValidationForUpdatePassword():
    token = request.args.get('token')
    payload = util.validateToken(token)
    #email = payload['userDetails']['email']
    return payload
    
    
    




############################# end of Android ##############################################

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=4004, debug=True)
