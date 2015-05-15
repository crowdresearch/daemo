__author__ = 'Megha'

import csv

__MODULE_NAME__ = 6
__FILE__ = 'meghaWorkerData.txt'

def read_file (__FILE__):
    counter = 0
    with open(__FILE__) as fp:
        for line in fp:
            print line

if __name__ == '__main__':
    read_file(__FILE__)