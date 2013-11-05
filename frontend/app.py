#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
import urllib2
import logging.handlers
import datetime
import flask
import admin
import share

app = flask.Flask(__name__)
app.register_blueprint(admin.app, url_prefix="/_admin")
app.register_blueprint(share.app, url_prefix="/<share_id>")
handler = logging.handlers.RotatingFileHandler("/var/log/oscar/app.log", 'a', 1024*1024*100,9)
app.logger.addHandler(handler)

import oscar

private_address_regex = re.compile(r"(^127\.0\.0\.1)|(^10\.)|(^172\.1[6-9]\.)|(^172\.2[0-9]\.)|(^172\.3[0-1]\.)|(^192\.168\.)")

def _recent(share_id, path_prefix = "/"):
    results = oscar.get("/file/%s/recent" % share_id, {"path_prefix":path_prefix})
    for result in results:
        result["suggested_filetype"] = oscar.suggest_filetype(result["name"])
    return (len(results), results)

@app.template_filter("build_path_link")
def build_path_link(share_id, path=None, filename=None):
    share_id = re.sub(r'^/+','',share_id)
    if path: path = re.sub(r'^/+','',path)
    if filename: filename = re.sub(r'^/+','',filename)
    if path != None and filename != None:
        return os.path.normpath(os.path.join('/',share_id,path,filename))
    if path != None:
        return os.path.normpath(os.path.join('/',share_id,path)) + '/'
    #else
    return os.path.normpath(os.path.join('/',share_id)) + '/'

@app.template_filter("datetime_string")
def datetime_string(t):
    now = datetime.datetime.fromtimestamp(t / 1000.0)
    return now.strftime(u"%Y-%m-%d %H:%M")

@app.template_filter("size_string")
def size_string(size):
    if size > 1024 * 1024 * 1024 * 1024:
        return "%.1fTB"  % (size / (1024 * 1024 * 1024 * 1024.0))
    if size > 1024 * 1024 * 1024:
        return "%.1fGB"  % (size / (1024 * 1024 * 1024.0))
    if size > 1024 * 1024:
        return "%.1fMB"  % (size / (1024 * 1024.0))
    if size > 1024:
        return "%.1fKB"  % (size / 1024.0)
    return u"%dバイト" % size

@app.before_request
def before_request():
    # eden == MSIE in private network
    flask.g.eden = "MSIE " in flask.request.headers.get('User-Agent') and private_address_regex.match(flask.request.remote_addr)
    flask.g.username = flask.request.authorization.username if flask.request.authorization else None

@app.route("/")
def index():
    shares = oscar.get_share_list()
    counts = {}
    for share in shares:
        share_id = share[0]
        try:
            count = oscar.get("/file/%s/count" % share_id, {"path_prefix":'/'})[0]
            counts[share_id] = count
        except urllib2.HTTPError, e:
            app.logger.exception("/file/{share_id}/count")
            app.logger.error(e.read())
            return flask.render_template("error.html")

    st = os.statvfs("/")

    def capacity_string(nbytes):
        if nbytes >= 1024 * 1024 * 1024 * 1024:
            return "%.1fTB" % (nbytes / (1024 * 1024 * 1024 * 1024.0))
        if nbytes >= 1024 * 1024 * 1024:
            return "%.1fGB" % (nbytes / (1024 * 1024 * 1024.0))
        if nbytes >= 1024 * 1024:
            return "%.1fMB" % (nbytes / (1024 * 1024.0))

    free_bytes = st.f_bavail * st.f_frsize
    total_bytes = st.f_blocks * st.f_frsize
    used_bytes = (st.f_blocks - st.f_bfree) * st.f_frsize
    used = ( capacity_string(used_bytes), used_bytes * 100 / total_bytes )
    free = ( capacity_string(free_bytes), 100 - used[1] )
    total = ( capacity_string(total_bytes), 100 )

    return flask.render_template("index.html", shares=shares,counts=counts, free=free, total=total, used=used, loadavg=os.getloadavg())

@app.route("/a/<size>")
def a(size):
    return oscar.get("/ad/ad%s-bs3" % size)[0]

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
