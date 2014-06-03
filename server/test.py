#coding:utf-8
import subprocess
import os
filename='gpx/1703714.gpx'
print(filename)
subprocess.call('gpx2shp %s'%(filename), shell=True)

