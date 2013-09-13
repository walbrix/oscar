#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import os
import re
import subprocess
import hashlib
import argparse
import oscar

def run():
    conn = oscar.connect_mysql()
    cur = conn.cursor()
    cur.execute("select get_lock(%s,%s)", ("indexing.lock",30))
    if cur.fetchone()[0] != 1: return False

    queue = oscar.get("/indexing/")
    for indexing_target in queue:
        file_id = indexing_target[0]
        path = indexing_target[1]
        unoconv = subprocess.Popen(["/usr/bin/unoconv","-f","html","--stdout",(oscar.base_dir + path).encode("utf-8")], shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        html, stderrdata = unoconv.communicate()
        if unoconv.wait() != 0:
            print stderrdata
            print oscar.post("/indexing/%s/fail" % file_id, {})
            continue
        lynx = subprocess.Popen(["/usr/bin/lynx","-stdin","-dump"],shell=False,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        text, stderrdata = lynx.communicate(html)
        if lynx.wait() != 0:
            print stderrdata
            print oscar.post("/indexing/%s/fail" % file_id, {})
            continue
        #else
        print oscar.post("/file/%s" % file_id, text, "text/plain")
        oscar.delete("/indexing/%s" % file_id)
        
    cur.close()
    conn.close()

if __name__ == '__main__':
    run()
