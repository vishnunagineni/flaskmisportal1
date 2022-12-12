# import os
# azure machine 
# basepath = "//20.219.146.33//SafeDigStorage"

# for .30 storage
basepath = "//20.219.146.33//SafeDigStorage"

# for ibiza machine
# SafeDigStorage = "//ZE42-V-IBIZADB1/SafeDigStorage/dataset"

# for local machine
SafeDigStorage = "C:/Users/MS59580/Desktop/safedig++/SafeDigStorage"
# SafeDigStorage = os.environ['MWS_ENV']+"/safedigplusplus/SafeDigStorage"
# localTempPath = "C:/Users/MS59580/Desktop/cloud/MWS_temp_data"


configuration = {
    "safeDigPack" :  "/dataset",
    # "mailOutput" : localTempPath + "/outlook/output"
    # "mailOutput": "C:/Users/MS59580/Desktop/backUp21/backendMailIo"
    "mailOutput": "//ZE42-V-IBIZADB1/SafeDigStorage/safedig++/MWS_temp_data/outlook/output"
}

SECRET = "Manish_Kumar_Sah"

#sender mail

# sender mail
#senderMail = "noreply.safedigAI@gmail.com"
senderMail = "vishnu.nagineni@zensar.com"
gmailPassword="fayzmywbqmxeayfd"
outlookPassword = "Zxcvbnm@59575"
resetPasswordUrl = "http://localhost:4200/update"


# collections name

jobsQueueCollectionName = "jobsQueue"
teamCollectionName = "team"
fileCollectionName = "files"
logCollectionName = "logs"


# Azure db
host = "20.219.146.33"
port = 27017
username = "zenadmin"
password = "zenadmin123"
dbName = "MWS-Version-2"

