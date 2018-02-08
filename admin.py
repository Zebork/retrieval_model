# -*- coding:utf-8 -*-

"""
Usage:
    admin.py <mode> [-a ASYNC]
    admin.py <mode> -f|--force
    admin.py <mode>
Options:
    -f --force          force do
    -h                  show help

Example:
    admin.py spider -a depart
    admin.py spider -a patch
    admin.py spider -a autorun
    admin.py invert
    admin.py invert -f
    admin.py start

"""

from docopt import docopt
import os
import controller
from controller import *
from multiprocessing import Process
from utils.db_connecter import db_connecter
import sys


def start_api():
    os.system("python web_sock.py 127.0.0.1:50000")
def start_django():
    os.chdir('./web_retrieval')
    os.system("python manage.py runserver 0.0.0.0:6061")

def main():
    arguments = docopt(__doc__, version="Naval Fate 2.0")
    mode = arguments["<mode>"]
    if mode == "spider":
        if arguments["-a"]:
            order = arguments['ASYNC']
            if order == "autorun":
                controller.toutiao_spider(mode=1)
                controller.tencent_spider(mode=1)
            elif order == "depart":
                controller.toutiao_spider(mode=2)
                controller.tencent_spider(mode=2)
            elif order == "patch":
                controller.toutiao_spider(mode=3)
                controller.tencent_spider(mode=3)
    elif mode == "start":
        if arguments["--force"]:
            print 'Start unsupport force '
            return
        Process(target=start_api).start()
        Process(target=start_django).start()
    elif mode == "invert":
        if not  arguments["--force"]:
            if controller.check_not_null():
                print "inverted has been done. If you want redo somehow, use -f"
                return
        else:
            controller.delete_inverted()
        controller.invert_redo()
if __name__ == "__main__":
    main()