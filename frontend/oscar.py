# -*- coding: utf-8 -*-

import os
import urllib
import urllib2
import httplib2
import json
try:
    import MySQLdb
except:
    pass

api_root="http://localhost:8080/oscar/"
mysql_host="localhost"
mysql_db="oscar"
mysql_user="oscar"
mysql_password=""

__CONFIG_FILE = os.path.splitext(__file__)[0] + ".conf"
if os.path.exists(__CONFIG_FILE):
    for key,value in json.load(open(__CONFIG_FILE, "r")).items():
        globals()[key] = value

# unicode文字列入りのdictを都合のいいバイト列に直す
def encoded_dict(in_dict):
    out_dict = {}
    for k, v in in_dict.iteritems():
        if isinstance(v, unicode):
            v = v.encode('utf8')
        elif isinstance(v, str):
            # Must be encoded in UTF-8
            v.decode('utf8')
        out_dict[k] = v
    return out_dict
 
# GETメソッドを実行し、返値をJSONデコードして返す
def get(func, params = {}):
    url = api_root + "/" + func
    if params != None and len(params) > 0:
        url += "?" + urllib.urlencode(encoded_dict(params))
    return json.load(urllib2.urlopen(url))
 
# POSTメソッドを実行し、返値をJSONデコードして返す。
# 第三引数はリクエストのcontent_typeで、これと実際に与えられたparamsの型の組み合わせに
# 応じて適当に変換をする。
def post(func, params, content_type = "application/x-www-form-urlencoded"):
    headers={'Content-type': content_type}
    if isinstance(params, dict) or isinstance(params, list):
        if content_type == "application/json":
            request_body = json.dumps(params)
        else:
            request_body = urllib.urlencode(encoded_dict(params))
    elif isinstance(params, unicode):
        request_body = params.encode("utf-8")
    elif isinstance(params, file):
        request_body = params.read()
    elif isinstance(params, str):
        request_body = bytearray(params)
    else:
        request_body = str(params)
 
    req = urllib2.Request(api_root + "/" + func, data=request_body, headers={'Content-type': content_type})
    return json.load(urllib2.urlopen(req))

def delete(func, params={}):
    http = httplib2.Http()
    url = api_root + "/" + func
    if params != None and len(params) > 0:
        url += "?" + urllib.urlencode(encoded_dict(params))
    response, content = http.request(url, "DELETE")
    return json.loads(content)

def connect_mysql():
    return MySQLdb.connect(host=mysql_host,db=mysql_db,user=mysql_user,passwd=mysql_password)
