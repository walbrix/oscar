# -*- coding: utf-8 -*-

import os
import urllib
import urllib2
import httplib2
import json
import ConfigParser
import binascii

try:
    import tdb
    import smbpasswd
    import MySQLdb
except:
    pass

smb_conf = "/etc/samba/smb.conf"
smb_passdb = "/var/lib/samba/private/passdb.tdb"
groonga_executable = "/usr/local/bin/groonga"
mroonga_db = "/var/lib/mysql/oscar.mrn"
run_dir = "/run/oscar"
api_root="http://localhost:8080/trunk/"
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
    print func
    url = api_root + "/" + urllib.quote(func)
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
 
    req = urllib2.Request(api_root + "/" + urllib.quote(func), data=request_body, headers={'Content-type': content_type})
    return json.load(urllib2.urlopen(req))

def delete(func, params={}):
    http = httplib2.Http()
    url = api_root + "/" + urllib.quote(func)
    if params != None and len(params) > 0:
        url += "?" + urllib.urlencode(encoded_dict(params))
    response, content = http.request(url, "DELETE")
    return json.loads(content)

def connect_mysql():
    return MySQLdb.connect(host=mysql_host,db=mysql_db,user=mysql_user,passwd=mysql_password)

class JobLock():
    def __init__(self, lock_name, timeout=30):
        self.lock_name = lock_name
        self.timeout = timeout
    def __enter__(self):
        self.conn = MySQLdb.connect(host=mysql_host,db=mysql_db,user=mysql_user,passwd=mysql_password)
        self.cur = self.conn.cursor()
        self.cur.execute("select get_lock(%s,%s)", (self.lock_name,self.timeout))
        return self.cur.fetchone()[0] == 1
    def __exit__(self, exc_type, exc_value, traceback):
        self.cur.close()
        self.conn.close()
        if exc_type: return False
        return True

def _get_smb_conf_parser():
    parser = ConfigParser.SafeConfigParser({"guest ok":"no"})
    parser.read(smb_conf)
    return parser

def _get_share(parser, share_id):
    if not parser.has_section(share_id): return None
    path = parser.get(share_id, "path")
    guest_ok = parser.getboolean(share_id, "guest ok")
    comment = (parser.get(share_id, "comment") if parser.has_option(share_id, "comment") else ("共有フォルダ" if guest_ok else "アクセス制限された共有フォルダ")).decode("utf-8")
    return (share_id, path, guest_ok,comment)

def get_share(share_id):
    parser = _get_smb_conf_parser()
    return _get_share(parser, share_id)

def get_share_list():
    parser = _get_smb_conf_parser()
    share_list = []
    for section in filter(lambda x:x not in ["global","homes","printers"], parser.sections()):
        share_list.append(_get_share(parser,section))
    return share_list

def suggest_filetype(filename):
    types = {
        ".xls":"xls",
        ".xlsx":"xls",
        ".ppt":"ppt",
        ".pptx":"ppt",
        ".pdf":"pdf",
        ".html":"html",
        ".htm":"html",
        ".doc":"doc",
        ".docx":"doc",
        ".txt":"txt",
        ".csv":"csv"
    }
    suffix = os.path.splitext(filename)[1]
    if suffix.lower() not in types: return None
    return types[suffix.lower()]

def touch_run_file(filename):
    fullpath = os.path.join(run_dir, filename)
    with open(fullpath, "a"):
        os.utime(fullpath, None)

def check_run_file(filename):
    fullpath = os.path.join(run_dir, filename)
    return os.path.isfile(fullpath)

def remove_run_file(filename):
    fullpath = os.path.join(run_dir, filename)
    if os.path.isfile(fullpath):
        os.unlink(fullpath)
        return True
    return False

def request_perform_walk():
    touch_run_file("perform_walk")

def request_perform_cleanup():
    touch_run_file("perform_cleanup")

def check_smb_passwd(username, passwd):
    passdb = tdb.open(smb_passdb)
    try:
        user_record = passdb.get("USER_%s\x00" % username.lower())
        if not user_record: return False
        return binascii.a2b_hex(smbpasswd.nthash(passwd)) in user_record
    finally:
        passdb.close()
