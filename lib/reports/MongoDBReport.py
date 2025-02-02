# -*- coding: utf-8 -*-
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#  Author: Mauro Soria

import json

from lib.reports import *
from pymongo import MongoClient

report_db = MongoClient().get_database('dirsearch').get_collection('report')


class MongoDBReport(BaseReport):

    def addPath(self, path, status, response):
        contentLength = None

        try:
            contentLength = int(response.headers['content-length'])

        except (KeyError, ValueError):
            contentLength = len(response.body)

        self.pathList.append((path, status, contentLength, response.redirect))

    def save(self):
        headerName = '{0}://{1}:{2}/{3}'.format(self.protocol, self.host, self.port, self.basePath)
        for path, status, contentLength, redirect in self.pathList:
            url = '{}{}'.format(headerName, path)
            entry = {'status': status, 'path': path, 'content-length': contentLength, 'redirect': redirect,
                     'url': url, 'host': self.host}
            try:
                report_db.update_one({'url': url}, {'$set': entry}, upsert=True)
            except:pass

    def generate(self):
        headerName = '{0}://{1}:{2}/{3}'.format(self.protocol, self.host, self.port, self.basePath)
        result = {headerName: []}

        for path, status, contentLength, redirect in self.pathList:
            entry = {'status': status, 'path': path, 'content-length': contentLength, 'redirect': redirect}
            result[headerName].append(entry)

        return json.dumps(result, sort_keys=True, indent=4)
