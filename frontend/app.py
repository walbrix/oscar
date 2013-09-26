#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
import urllib2
import logging.handlers
import datetime
import flask

app = flask.Flask(__name__)
handler = logging.handlers.RotatingFileHandler("/var/log/oscar/app.log", 'a', 1024*1024*100,9)
app.logger.addHandler(handler)

import oscar
import search

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

@app.route("/<share_id>/", defaults={"path":""})
@app.route("/<share_id>/<path:path>/")
def dir(share_id, path):
    share = oscar.get_share(share_id)
    if share == None: return "not found", 404

    real_path = os.path.join(share[1], path)
    if not os.path.isdir(real_path): return "not found", 404
    if not os.access(real_path ,os.R_OK|os.X_OK): return "Permission denied", 403

    path_elements = []
    if path != "":
        for d in path.split('/'):
            if len(path_elements) == 0:
                path_elements.append((d, d))
            else:
                path_elements.append((d, os.path.join(path_elements[-1][1], d)))
    
    count = oscar.get("/file/%s/count" % share_id, {"path_prefix":'/' + path})[0]
    q = flask.request.args.get("q")
    results = search.mroonga_search(share, q, '/' + path) if q else None

    root, dirs, files = next(os.walk(real_path))
    dirs = filter(lambda x:not x.startswith('.'), map(lambda x:x if isinstance(x,unicode) else x.decode("utf-8"), dirs))
    files = filter(lambda x:not x.startswith('.'), map(lambda x:x if isinstance(x,unicode) else x.decode("utf-8"), files))
    return flask.render_template("dir.html",dirs=dirs,files=files,count=count,share_id=share_id,path=path,path_elements=path_elements,results=results,q=q)

@app.route('/<share_id>/search', defaults={'path': ''})
@app.route("/<share_id>/<path:path>/search")
def _search(share_id, path):
    share = oscar.get_share(share_id)
    if share == None: return "not found", 404

    q = flask.request.args.get("q")
    results = search.mroonga_search(share, q, '/' + path)
    return flask.render_template("results.html", q=q, share_id=share_id,results=results)

@app.route('/<share_id>/dups.html')
def dups(share_id):
    dups = oscar.get("/file/%s/dups" % share_id)
    return flask.render_template("dups.html", share_id=share_id, dups=dups)

@app.route('/<share_id>/<filename>', defaults={'path': ''})
@app.route("/<share_id>/<path:path>/<filename>")
def file(share_id, path,filename):
    if share_id == "static":
        return flask.send_from_directory(os.path.join(app.root_path, "static", path), filename)
    share = oscar.get_share(share_id)
    return flask.send_from_directory(os.path.join(share[1], path), filename)

@app.route("/_admin/")
def admin():
    return flask.render_template("admin.html")

@app.route("/_admin/indexing.html")
def admin_indexing():
    awaiting = oscar.get("/indexing/", {"limit":100})
    failed = oscar.get("/indexing/recent_failed", {"limit":100})
    return flask.render_template("indexing.html", awaiting=awaiting,failed=failed)

@app.route("/_admin/request_sync", methods=['POST'])
def admin_request_sync():
    oscar.request_perform_cleanup()
    oscar.request_perform_walk()
    return flask.jsonify(result=True)

@app.route("/_admin/reset_database", methods=['POST'])
def admin_reset_database():
    result = oscar.post("/admin/RESET", {})[0]
    oscar.request_perform_walk()
    return flask.jsonify(result=result)

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
