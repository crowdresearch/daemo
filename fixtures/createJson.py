__author__ = 'Megha'
# Script to transfer csv containing data about various models to json
# Input csv file constituting of the model data
# Output json file representing the csv data as json object
# Assumes model name to be first line
# Field names of the model on the second line
# Data seperated by __DELIM__
# Example:
# L01 ModelName: registrationmodel
# L02 FieldNames: user,activation_key,created_timestamp,last_updated
# L03 Data: 1,qwer,2015-05-01T00:17:40.085Z,2015-05-01T00:17:40.085Z
# L04 Data: 2,assd,2015-05-01T00:17:40.085Z,2015-05-01T00:17:40.085Z

import numpy as np
import pandas as pd
import json as json

__MODULE_NAME__ = 7  # Number of lines after which Model Name
__INPUT_FILE__ = 'meghaWorkerData.csv'
__OUTPUT_FILE__ = 'meghaWorkerData.json'
__NEWLINE__ = '\n'
__KEY1__ = 0
__KEY2__ = 0
__DELIM__ = ','
__APPEND__ = 'crowdsourcing.'
__KEY_MODEL__ = 'model'
__KEY_FIELDS__ = 'fields'
__KEY_PK__ = 'pk'


def create_dict(input_dict, module, data_collection):
    for key, value in input_dict.items():
        data_dict = {}
        data_dict[__KEY_FIELDS__] = value
        data_dict[__KEY_PK__] = key
        data_dict[__KEY_MODEL__] = __APPEND__ + module
        data_collection.append(data_dict)
    return data_collection


def create_data_json(file):
    in_fp = open(file, 'rb')
    file_lines = in_fp.readlines()
    in_fp.close()
    data_collection = []
    for line_no in range(0, len(file_lines)):
        if line_no % __MODULE_NAME__ == 0:
            columns = file_lines[line_no + 1].strip(__NEWLINE__).split(__DELIM__)
            instance1 = file_lines[line_no + 2].strip(__NEWLINE__).split(__DELIM__)
            instance2 = file_lines[line_no + 3].strip(__NEWLINE__).split(__DELIM__)
            instance3 = file_lines[line_no + 4].strip(__NEWLINE__).split(__DELIM__)
            instance4 = file_lines[line_no + 5].strip(__NEWLINE__).split(__DELIM__)
            instance5 = file_lines[line_no + 6].strip(__NEWLINE__).split(__DELIM__)
            data = np.array([instance1, instance2, instance3, instance4, instance5])
            df = pd.DataFrame(data, columns=columns)
            create_dict(df.transpose().to_dict(), file_lines[line_no].strip(__NEWLINE__), data_collection)
            del (df)
    print(data_collection)
    out_fp = open(__OUTPUT_FILE__, 'wb')
    out_fp.write(json.dumps(data_collection, indent=2))
    out_fp.close()


if __name__ == '__main__':
    create_data_json(__INPUT_FILE__)
