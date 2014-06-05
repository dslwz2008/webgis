#-*-coding:utf-8-*-
__author__ = 'shenshen'

import os
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
import json
import subprocess
import requests

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "template_path": os.path.join(os.path.dirname(__file__), "templates")
}

prj_str = '''GEOGCS["WGS 84",
  DATUM["World Geodetic System 1984",
    SPHEROID["WGS 84", 6378137.0, 298.257223563, AUTHORITY["EPSG","7030"]],
    AUTHORITY["EPSG","6326"]],
  PRIMEM["Greenwich", 0.0, AUTHORITY["EPSG","8901"]],
  UNIT["degree", 0.017453292519943295],
  AXIS["Geodetic longitude", EAST],
  AXIS["Geodetic latitude", NORTH],
  AUTHORITY["EPSG","4326"]]
'''

class FileUploadHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', "http://localhost:63342")
    def get(self):
        self.write('please use post.')
    def post(self):
        result = {}
        if self.request.files:
            gpxfile = self.request.files['gpxfile'][0]
            filename = 'gpx/' + gpxfile['filename']
            with open(filename, 'w') as fp:
                fp.write(gpxfile['body'])

            #convert GPX file to shapefile
            subprocess.call('gpx2shp %s' % (filename,), shell=True)
            #zip compress
            os.chdir('gpx')
            #remove gpx/ & .gpx extension
            postfix = '_trk'
            basename = filename[4:-4] + postfix
            prjname = basename + '.prj'
            #add prj file
            with open(prjname, 'w') as fp:
                fp.write(prj_str)

            zipname = basename + '.zip'
            shpname = basename + '.shp'
            shxname = basename + '.shx'
            dbfname = basename + '.dbf'
            command = 'zip %s %s %s %s %s' % (zipname, shpname, shxname, dbfname, prjname)
            subprocess.call(command, shell=True)
            os.chdir('..')

            #publish shapefile with new datastore in webgis workspace
            if self.new_ds_shape(basename, 'gpx/' + zipname) != 201:
                result['status'] = 'error'
                result['reason'] = 'create datastore failed'
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(result))
            #get featuretype of new layer, get bounding box
            ft_str = self.get_ft(basename, basename)
            if ft_str is None:
                result['status'] = 'error'
                result['reason'] = 'get feature type failed'
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(result))

            bbox = self.get_bounding_box(ft_str)
            #return bounding box
            result['status'] = 'ok'
            result['left'] = bbox[0]
            result['right'] = bbox[1]
            result['bottom'] = bbox[2]
            result['top'] = bbox[3]
            result['layername'] = basename
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(result))
        else:
            result['status'] = 'error'
            result['reason'] = 'no file uploaded'
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(result))

    def new_ds_shape(self, dsname, zipname):
        myUrl = 'http://192.168.36.5:8080/geoserver/rest/workspaces/webgis/datastores/%s/file.shp' \
                % (dsname,)
        with open(zipname, 'rb') as fp:
            payload = fp.read()
            headers = {'Content-type': 'application/zip'}
            resp = requests.put(myUrl, auth=('admin', 'geoserver'),
                                data=payload, headers=headers)
            print(resp.status_code)
            return resp.status_code

    def get_ft(self, dsname, lyrname):
        myUrl = 'http://192.168.36.5:8080/geoserver/rest/workspaces/webgis/datastores/%s/featuretypes/%s' \
                % (dsname, lyrname)
        headers = {'Accept': 'text/xml'}
        resp = requests.get(myUrl, auth=('admin','geoserver'),headers=headers)
        if resp.status_code == 200:
            print(resp.status_code)
            return resp.text
        return None

    # return bbox in order : [left, right, bottom, top]
    def get_bounding_box(self, xml):
        import xml.etree.cElementTree as ET
        root = ET.fromstring(xml)
        # print(root.tag)
        bbox = []
        for child in root.find('latLonBoundingBox')[:4]:
            bbox.append(float(child.text))
        print(bbox)
        return bbox


class IndexHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render('index.html')


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[(r'/fileupload', FileUploadHandler),
            (r'/index', IndexHandler),
            ], **settings
            )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
