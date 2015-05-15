__author__ = 'Megha'

import numpy as np
import pandas as pd
import simplejson as json
import copy

__MODULE_NAME__ = 7
__INPUT_FILE__ = 'meghaWorkerData.txt'
__OUTPUT_FILE__ = 'meghaWorkerData.json'
__NEWLINE__ = '\n'
__KEY1__ = 0
__KEY2__ = 0
__DELIM__ = ','

def key_to_string(input_dict):
    return dict((str(key), value) for key, value in input_dict.items())

def create_data_json(__FILE__):
    module_dict = {}
    data_dict = {}
    in_fp = open(__INPUT_FILE__, 'rb')
    file_lines = in_fp.readlines()
    in_fp.close()
    print len(file_lines)
    for line_no in range(0, len(file_lines)):
        if line_no % __MODULE_NAME__ == 0:
            columns = file_lines[line_no + 1].strip(__NEWLINE__).split(__DELIM__)
            instance1 = file_lines[line_no + 2].strip(__NEWLINE__).split(__DELIM__)
            instance2 = file_lines[line_no + 3].strip(__NEWLINE__).split(__DELIM__)
            instance3 = file_lines[line_no + 4].strip(__NEWLINE__).split(__DELIM__)
            instance4 = file_lines[line_no + 5].strip(__NEWLINE__).split(__DELIM__)
            instance5 = file_lines[line_no + 6].strip(__NEWLINE__).split(__DELIM__)
            data = np.array([instance1,instance2,instance3,instance4,instance5])
            df = pd.DataFrame(data, columns = columns)
            module_dict[file_lines[line_no].strip(__NEWLINE__)] = df.to_dict()
            del(df)
    print module_dict
    dict_copy = copy.deepcopy(module_dict)
    for module in module_dict:
        for data in module_dict[module]:
            dict_copy[module][data] = key_to_string(module_dict[module][data])
    out_fp = open(__OUTPUT_FILE__, 'wb')
    out_fp.write(json.dumps(dict_copy, indent = 2))
    out_fp.close()

if __name__ == '__main__':
    create_data_json (__INPUT_FILE__)