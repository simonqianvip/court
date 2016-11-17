# -*- coding: utf-8 -*-
import os, sys
import urllib
import win32com
from win32com.client import Dispatch, constants


# class Rename(object):
def changeFileName(dir):
    """
    1,获取下载文件的属性(时间),获取前台页面的文章标题
    2,
    :param dir:
    :return:
    """
    file_pre = 'd:\\court_Download\\'
    filenames = os.listdir(dir)
    w = win32com.client.Dispatch('Word.Application')
    w.Visible = True
    w.DisplayAlerts = 0

    for f in filenames:
        name = urllib.unquote(f)
        print name
        # 获取文件的属性
        file_info = os.stat(file_pre+f)
        doc = w.Documents.Open(dir +"\\"+ f)
        print(doc.Content)

        # print(name)
        # print filenames[2]
        # for a in xrange(len(filenames)):
        # print dir + os.sep + f
        # os.rename(dir + os.sep + f, dir + os.sep + name)


# def readDoc(fileName):


if __name__ == '__main__':
    # rename = Rename()
    changeFileName('d:\\court_Download')
