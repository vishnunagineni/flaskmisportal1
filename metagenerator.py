import argparse
import os
import json
from logging_config import logging
from map_warnings_ai import inputfunction
import re
import pandas as pd

logger = logging.getLogger(__name__)

# ap = argparse.ArgumentParser()
# ap.add_argument("-d", "--dir", type=str,
#                 help="base folder path")

# args = vars(ap.parse_args())

# if args['dir'] != None:
#     rootdir = args['dir']

    # print([z for x,y,z in os.walk('./../data')])


def subdirs(path):
    """Yield directory names not starting with '.' under given path."""
    structList = []
    for entry in os.scandir(path):
        if not entry.name.startswith('.') and entry.is_dir():
            # This is a folder
            for root, dirs, files in os.walk(entry):
                outfileName = os.path.join(root, "indexmeta.json")  # hardcoded path
                # folderOut = open(outfileName, 'w')
                print("outfileName is " + outfileName)
                structure = []
                for f in files:
                    filePath = os.path.join(root, f)
                    print(filePath)
                    assettype, embed_warning = identifyAssetType(f, root)
                    structure.append(
                        {
                            "filename": f,
                            "filepath": filePath,
                            "asset_type": assettype,
                            "warning_text": embed_warning
                        })
                # with open(outfileName, 'w', encoding='utf-8') as f:
                #     json.dump(structure, f, ensure_ascii=False, indent=4)
                prepare_excel_output(json.dumps(structure), root)  # hardcoded path)
                structList.append(structure)

            # folderOut.close()
        else:
            print("Provide the path of the parent folder, you need to run this script on")
    return structList
def runAIModel_MapWarnings(filename_pdf, utility_type, basepath):
    warning_dict=inputfunction(filename_pdf,utility_type, basepath)
    return warning_dict['Gas']


def identifyAssetType(filename, basepath):
    print(filename)
    m = re.search("CadentGas.pdf", filename, re.IGNORECASE)
    if m:
        print(m.group(0))
        warning_text=runAIModel_MapWarnings(filename, "Gas",basepath)
        return "Gas", warning_text
    else:
        return "", ""


def prepare_excel_output(inputjson,outputbasefolder):
    df = pd.read_json(inputjson)
    print(df)
    outputexcel= os.path.join(outputbasefolder, "indexmeta.xlsx")
    try:
        df.to_excel(outputexcel)
    except Exception as ex:
        print(str(ex))
        df.to_excel(os.path.join(outputbasefolder,"output-error.xlsx"))


# if __name__ == '__main__':
#     subdirs(rootdir)
