#coding:utf-8
import subprocess
import os
import requests

# filename='gpx/1703714.gpx'
# print(filename)
# subprocess.call('gpx2shp %s'%(filename), shell=True)

def query_ws():
    myUrl = 'http://192.168.36.5:8080/geoserver/rest/namespace'
    headers = {'Accept': 'text/xml'}
    resp = requests.get(myUrl, auth=('admin', 'geoserver'), headers=headers)
    fp = open('test.xml','w')
    fp.write(resp.text)
    fp.close()


def create_ws():
    myUrl = 'http://192.168.36.5:8080/geoserver/rest/namespaces'
    fp = open('test.xml', 'r')
    payload = fp.read()
    headers = {'Content-type': 'text/xml'}
    resp = requests.post(myUrl, auth=('admin', 'geoserver'),
                         data=payload, headers=headers)
    print(resp.status_code)

def get_dss():
    myUrl = 'http://192.168.36.5:8080/geoserver/rest/workspaces/topp/datastores'
    headers = {'Accept': 'text/xml'}
    resp = requests.get(myUrl, auth=('admin','geoserver'),headers=headers)
    fp = open('test.xml','w')
    fp.write(resp.text)
    fp.close()

def new_ds_shape(name, desc, filename, ns):
    config = '''<dataStore>
         <name>%s</name>
         <description>%s</description>
         <type>Shapefile</type>
         <enabled>true</enabled>
         <connectionParameters>
           <entry key="memory mapped buffer">false</entry>
           <entry key="create spatial index">true</entry>
           <entry key="charset">UTF-8</entry>
           <entry key="filetype">shapefile</entry>
           <entry key="cache and reuse memory maps">true</entry>
           <entry key="url">file://%s</entry>
           <entry key="namespace">%s</entry>
         </connectionParameters>
         <__default>false</__default>
       </dataStore>''' % (name, desc, filename, ns)
    myUrl = 'http://192.168.36.5:8080/geoserver/rest/workspaces/webgis/datastores/'

    headers = {'Content-type': 'text/xml','Accept': 'text/xml'}
    resp = requests.post(myUrl, auth=('admin', 'geoserver'),
                         data=config, headers=headers)
    print(resp.status_code)


def new_ds_shape1(filename):
    myUrl = 'http://192.168.36.5:8080/geoserver/rest/workspaces/webgis/datastores/test111/file.shp'
    fp = open(filename, 'rb')
    payload = fp.read()
    headers = {'Content-type': 'application/zip'}
    resp = requests.put(myUrl, auth=('admin', 'geoserver'),
                        data=payload, headers=headers)
    print(resp.status_code)


def get_fts():
    myUrl = 'http://192.168.36.5:8080/geoserver/rest/workspaces/webgis/datastores/tracks_bat/featuretypes'
    headers = {'Accept': 'text/xml'}
    resp = requests.get(myUrl, auth=('admin','geoserver'),headers=headers)
    fp = open('test.xml','w')
    fp.write(resp.text)
    fp.close()
    print(resp.status_code)

def get_ft():
    myUrl = 'http://192.168.36.5:8080/geoserver/rest/workspaces/webgis/datastores/testtrack/featuretypes/1703714_trk'
    headers = {'Accept': 'text/xml'}
    resp = requests.get(myUrl, auth=('admin','geoserver'),headers=headers)
    fp = open('featuretype.xml','w')
    fp.write(resp.text)
    fp.close()
    print(resp.status_code)
    return resp.text

def update_ft():
    myUrl = 'http://192.168.36.5:8080/geoserver/rest/workspaces/webgis/datastores/tracks_bat/featuretypes/testds?recalculate=nativebbox,latlonbbox'
    fp = open('featuretype.xml', 'r')
    payload = fp.read()
    headers = {'Content-type': 'text/xml'}
    resp = requests.post(myUrl, auth=('admin', 'geoserver'),
                         data=payload, headers=headers)
    print(resp.status_code)

def get_bounding_box():
    import xml.etree.cElementTree as ET
    root = ET.fromstring(read_xml())
    print(root.tag)
    bbox = []
    for child in root.find('latLonBoundingBox')[:4]:
        bbox.append(float(child.text))
    print(bbox)

def read_xml():
    with open('featuretype.xml', 'r') as fp:
        return fp.read()

if __name__ == '__main__':
    # query_ws()
    # create_ws()
    # get_ds()
    #new_ds_shape('testds', 'this is a test datastore',
    #             '/root/webgis/server/gpx/1703714_trk.shp',
    #             'http://192.168.36.5:8080/webgis')
    # get_fts()
    #get_ft()
    # new_ds_shape1('/root/webgis/server/gpx/1703714_trk.zip')
    # new_ds_shape1('/Users/shenshen/Downloads/GPSLogger/test111.zip')
    # update_ft()
    get_bounding_box()
