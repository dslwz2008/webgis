#-*-coding:utf-8-*-
__author__ = 'shenshen'

import urllib
import urllib2
import requests
import codecs

baseurl = 'http://api.openstreetmap.org/api/0.6/trackpoints?'
datapath = 'data/'

class BoundingBox(object):
    def __init__(self, left, bottom, right, top):
        self.left = left
        self.bottom = bottom
        self.right = right
        self.top = top

    def __str__(self):
        return '%s,%s,%s,%s' % (self.left, self.bottom, self.right, self.top)

    def name(self):
        return '%s_%s_%s_%s' % (self.left, self.bottom, self.right, self.top)


def fetch_trace():
    interval = 0.25
    #get page_count files every square
    page_count = 3
    # #data in north
    start = (80, 30)
    end = (116, 47)

    left = start[0]
    bottom = start[1]
    right = start[0]
    top = start[1]

    lon_range = (int)((end[0] - start[0]) / interval)
    lat_range = (int)((end[1] - start[1]) / interval)
    for lat in range(0, lat_range):
        top += interval
        for lon in range(0, lon_range):
            right += interval
            bbox = BoundingBox(left, bottom, right, top)
            print('getting bbox: %s \n' % str(bbox))
            for page_num in range(0, page_count):
                datafile = '%sdata_%s_%s.gpx' % (datapath, bbox.name(), str(page_num))
                params = urllib.urlencode({'bbox':str(bbox), 'page':page_num})
                r = requests.get(baseurl, params=params)
                with codecs.open(datafile, 'w', encoding='utf_8') as fh:
                    fh.write(r.text)
            left = right
        bottom = top
        left = right = start[0]

def clear_null_file():
    import os.path
    size = 0L
    for filename in os.listdir(datapath):
        if not filename.startswith('.'):
            if os.path.getsize(datapath + filename) == 130:
                os.remove(datapath + filename)


if __name__ == '__main__':
    # fetch_trace()
    clear_null_file()