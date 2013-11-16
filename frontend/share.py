# -*- coding: utf-8 -*-

import os
import sys
import re
import flask

import unirest

import oscar
import smbconf
import share
import search

app = flask.Blueprint(__name__, "share")

share_id_regex = re.compile(r'^/(.+)/')

@app.before_request
def before_request():
    share_id_match = share_id_regex.match(flask.request.path)
    if not share_id_match: return
    share_id = share_id_match.groups()[0]
    if not smbconf.share_exists(share_id): return
    share = smbconf.get_share(share_id)
    if share.guest_ok: return
    auth = flask.request.authorization
    if not auth or not oscar.check_smb_passwd(auth.username, auth.password):
        return flask.Response('You have to login with proper credentials', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

def _build_path_elements(path):
    path_elements = []
    if path != "":
        for d in path.split('/'):
            if len(path_elements) == 0:
                path_elements.append((d, d))
            else:
                path_elements.append((d, os.path.join(path_elements[-1][1], d)))
    return path_elements

@app.route("/", defaults={"path":""})
@app.route("/<path:path>/")
def dir(share_id, path):
    try:
        share = smbconf.get_share(share_id)
    except smbconf.NoSuchShareException:
        return "not found", 404

    real_path = share.real_path(path)
    if not os.path.isdir(real_path): return "not found", 404
    if not os.access(real_path ,os.R_OK|os.X_OK): return "Permission denied", 403

    path_elements = _build_path_elements(path)
    
    response = unirest.get(oscar.api_root + "file/%s/count" % share.urlencoded_name(), params={"path_prefix":'/' + path})
    count = response.body[0]
    q = flask.request.args.get("q")

    try:
        results = search.mroonga_search(share, q, '/' + path) if q else None
    except:
        flask.current_app.logger.exception("Search error")
        raise

    root, dirs, files = next(os.walk(real_path))
    dirs = filter(lambda x:not x.startswith('.'), map(lambda x:x if isinstance(x,unicode) else x.decode("utf-8"), dirs))
    files = filter(lambda x:not x.startswith('.'), map(lambda x:x if isinstance(x,unicode) else x.decode("utf-8"), files))
    return flask.render_template("dir.html",dirs=dirs,files=files,count=count,share_id=share_id,path=path,path_elements=path_elements,results=results,q=q)

@app.route('/search', defaults={'path': ''})
@app.route("/<path:path>/search")
def _search(share_id, path):
    try:
        share = smbconf.get_share(share_id)
    except smbconf.NoSuchShareException:
        return "not found", 404

    q = flask.request.args.get("q", default=None)
    
    if "XMLHttpRequest" in flask.request.headers.get('X-Requested-With', default=""):
        if q == None or q == "": return ""
        results = search.mroonga_search(share, q, '/' + path)
        return flask.render_template("results.html", q=q, share_id=share_id,results=results)
    else:
        limit = 20
        page =  flask.request.args.get("page", default=1, type=int)
        offset = (page - 1) * limit
        path_elements = _build_path_elements(path)
        if q == None or q == "": return flask.render_template("results-all.html", q=None, share_id=share_id,path_elements=path_elements,count=0,results=[],page=page,limit=limit)
        results = search.mroonga_search(share, q, '/' + path, offset, limit)
        return flask.render_template("results-all.html", q=q, share_id=share_id,path_elements=path_elements,count=results[0],results=results[1],page=page,limit=limit)

@app.route('/dups.html')
def dups(share_id):
    try:
        share = smbconf.get_share(share_id)
    except smbconf.NoSuchShareException:
        return "not found", 404

    response = unirest.get(oscar.api_root + "file/%s/dups" % share.urlencoded_name())
    if response.code != 200: raise oscar.RestException(response.code, response.raw_body)
    dups = response.body
    return flask.render_template("dups.html", share_id=share_id, dups=dups)

@app.route('/<filename>', defaults={'path': ''})
@app.route("/<path:path>/<filename>")
def file(share_id, path,filename):
    if share_id == "static":
        return flask.send_from_directory(os.path.join(app.root_path, "static", path), filename)
    share = smbconf.get_share(share_id)
    return flask.send_from_directory(share.real_path(path), filename.encode("utf-8"))
