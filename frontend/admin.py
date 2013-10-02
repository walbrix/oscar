# -*- coding: utf-8 -*-

import sys
import flask
import oscar
import admin

app = flask.Blueprint(__name__, "admin")

@app.before_request
def before_request():
    shares = oscar.get_share_list()
    if not any(map(lambda x:not x[2], shares)): return
    auth = flask.request.authorization
    if not auth or not oscar.check_smb_passwd(auth.username, auth.password):
        return flask.Response('You have to login with proper credentials', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

@app.route("/")
def admin():
    return flask.render_template("admin.html")

@app.route("/indexing.html")
def admin_indexing():
    awaiting = oscar.get("/indexing/", {"limit":100})
    failed = oscar.get("/indexing/recent_failed", {"limit":100})
    return flask.render_template("indexing.html", awaiting=awaiting,failed=failed)

@app.route("/request_sync", methods=['POST'])
def admin_request_sync():
    oscar.request_perform_cleanup()
    oscar.request_perform_walk()
    return flask.jsonify(result=True)

@app.route("/reset_database", methods=['POST'])
def admin_reset_database():
    result = oscar.post("/admin/RESET", {})[0]
    oscar.request_perform_walk()
    return flask.jsonify(result=result)
