# -*- coding: utf-8 -*-

import os
import sys
import re
import flask
import oscar
import share
import search

app = flask.Blueprint(__name__, "share")

share_id_regex = re.compile(r'^/(.+)/')

@app.before_request
def before_request():
    share_id_match = share_id_regex.match(flask.request.path)
    if not share_id_match: return
    share_id = share_id_match.groups()[0]
    share = oscar.get_share(share_id)
    if not share or share[2]: return
    auth = flask.request.authorization
    if not auth or not oscar.check_smb_passwd(auth.username, auth.password):
        return flask.Response('You have to login with proper credentials', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

@app.route("/", defaults={"path":""})
@app.route("/<path:path>/")
def dir(share_id, path):
    share = oscar.get_share(share_id)
    if share == None: return "not found", 404

    real_path = os.path.join(share[1], path.encode("utf-8"))
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
    share = oscar.get_share(share_id)
    if share == None: return "not found", 404

    q = flask.request.args.get("q")
    results = search.mroonga_search(share, q, '/' + path)
    return flask.render_template("results.html", q=q, share_id=share_id,results=results)

@app.route('/dups.html')
def dups(share_id):
    dups = oscar.get("/file/%s/dups" % share_id)
    return flask.render_template("dups.html", share_id=share_id, dups=dups)

@app.route('/<filename>', defaults={'path': ''})
@app.route("/<path:path>/<filename>")
def file(share_id, path,filename):
    if share_id == "static":
        return flask.send_from_directory(os.path.join(app.root_path, "static", path), filename)
    share = oscar.get_share(share_id)
    return flask.send_from_directory(os.path.join(share[1], path.encode("utf-8")), filename.encode("utf-8"))
