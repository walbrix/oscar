#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import subprocess
import json
import oscar
import unirest

def mroonga_search(share, q, path_prefix="/"):
    response = unirest.get(oscar.api_root + "file/%s/search" % share.urlencoded_name(), params={"q":q, "path_prefix":path_prefix})
    if response.code != 200: raise oscar.RestException(response.code, response.raw_body)

    results = response.body

    def transform(row):
        path = row[0]["path"]
        name = row[0]["name"]
        os_pathname = share.real_path(os.path.join(path, name))
        print os_pathname
        return {
            "id":row[0]["id"],
            "path":path,
            "name":name,
            "atime":row[0]["atime"],
            "ctime":row[0]["ctime"],
            "mtime":row[0]["mtime"],
            "size":row[0]["size"],
            "updated_at":row[0]["updated_at"],
            "path_snippets":row[1],
            "name_snippets":row[2],
            "contents_snippets":row[3],
            "suggested_filetype":oscar.suggest_filetype(row[0]["name"]),
            "available":os.path.isfile(os_pathname)
        }
    return (results[0], map(lambda row:transform(row), results[1]))

def groonga_search(share, q, path_prefix="/"):
    query = 'select files --match_columns path||name*10||contents*5 --output_columns "id,path,name,atime,ctime,mtime,size,sha1sum,updated_at,snippet_html(path),snippet_html(name),snippet_html(contents)" --command_version 2 --sortby -_score --filter "share_id==\'share\' && (path == \'/\' || path @^ \'/\')" --query "ppt"'
    groonga = subprocess.Popen([oscar.groonga_executable,oscar.mroonga_db], shell=False,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    stdoutdata, stderrdata = groonga.communicate(query)
    print stderrdata
    if groonga.wait() != 0: raise Exception(stderrdata)
    print stdoutdata
    return json.loads(stdoutdata)
