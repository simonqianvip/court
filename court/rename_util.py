import os, sys
import urllib
import win32com
from win32com.client import Dispatch, constants


# class Rename(object):
def changeFileName(dir):
    filenames = os.listdir(dir)
    w = win32com.client.Dispatch('Word.Application')
    w.Visible = True
    w.DisplayAlerts = 0

    for f in filenames:
        name = urllib.unquote(f)
        print(name)
        # doc = w.Documents.Open(dir +"\\"+ f)
        # print(doc.Content)

        # print(name)
        # print filenames[2]
        # for a in xrange(len(filenames)):
        #     os.rename(dir + os.sep + filenames[a], dir + os.sep + str(a) + '.doc')


# def readDoc(fileName):


if __name__ == '__main__':
    # rename = Rename()
    changeFileName('d:\\FireFox_Download')
