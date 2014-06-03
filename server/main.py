#-*-coding:utf-8-*-
__author__ = 'shenshen'

import os
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
import json
import subprocess

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "template_path": os.path.join(os.path.dirname(__file__), "templates")
}


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

            #new datastore in webgis workspace

            #publish with styles

            result['status'] = 'ok'
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(result))
        else:
            result['status'] = 'error'
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(result))


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
