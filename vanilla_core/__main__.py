#!/usr/bin/python3

# 分别以子程序的方式运行

import subprocess

subprocess.Popen(["python3", "./characteristic/api.py"])
subprocess.Popen(["python3", "./ocr/api.py"])