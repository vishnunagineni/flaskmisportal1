# import os
import config
import util
# from metagenerator import subdirs
# import pandas as pd
#import road_detection as rd
# import map_warnings_ai as map_Warnings
# import constant as const
# import road_segmentation as temp
# import warningModule as warningModule


############################ MERGED CODE ###################

def roasterDetails(roasterName, empId, email, machineId, password, role):

    memberDetails = {
        "name" : roasterName,
        "empId" : empId,
        "email":email,
        "password" : password,
        "machineName": machineId,
        "role":role
    }

    return memberDetails


##############################################################


###################### RPA ########################################################################

def indexFileToJson(jobCreationDate, jobId, easting, northing):
    indexFilePath = config.SafeDigStorage+"/"+jobCreationDate+"/"+jobId+"/"+easting+"_"+northing+"/"+"index.xlsx"
    print(indexFilePath)
    sheetName = 'Sheet1'
    readMode = 'rb'
    indexFileSheet = util.getWorkBookSheet(indexFilePath, sheetName, readMode)

    loopVar = 2
    fileList = []
    while(True):
        filename = indexFileSheet.cell(row=loopVar, column=1).value

        if filename is None:
            print("index of index file data")
            break
        else:
            utilityType = indexFileSheet.cell(row=loopVar, column=2).value
            warning = indexFileSheet.cell(row=loopVar, column=3).value
            # fileUrl = jobId+"/"+packId+"/"+filename
            fileUrl = jobCreationDate+"/"+jobId+"/"+easting+"_"+northing+"/"+filename

            loopVar = loopVar + 1

            fileDetails = {
                "fileName" : filename,
                "fileUrl" : fileUrl,
                "utilityType" : utilityType,
                "warnings" : warning,
                "comment":"NA",
                "fileReadTimeStamp":"NA"
            }

            fileList.append(fileDetails)

    return fileList

###########################  end of RPA ############################################################
