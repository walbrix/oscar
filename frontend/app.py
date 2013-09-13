#!/usr/bin/python
# -*- coding: utf-8 -*-
import flask

app = flask.Flask(__name__)
import oscar

@app.route('/info', defaults={'path': ''})
@app.route("/<path:path>/info")
def info(path):
    count = oscar.get("/file/count", {"path_prefix":'/' + path})[0]
    path_elements = path.split('/') if path != "" else []
    return flask.render_template("info.html", count=count, path_elements=path_elements)

@app.route('/search', defaults={'path': ''})
@app.route("/<path:path>/search")
def search(path):
    q = flask.request.args.get("q")
    results = oscar.get("/file/search", {"q":q})
    return u"<h4>'%s'の検索結果</h4>Hello World! %s %s" % (q, path, results)

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
