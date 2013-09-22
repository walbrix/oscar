#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import sys
import os
import re
import subprocess
import hashlib
import argparse
import nkf
import oscar
import officex

class IndexingFailureException(Exception):
    def __init__(self, str):
        self.str = str
    def __str__(self):
        return u"Indexing failure '%s'" % (self.str)

def unoconv(os_pathname):
    uc = subprocess.Popen(["/usr/bin/unoconv","-f","html","--stdout",os_pathname], shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    html, stderrdata = uc.communicate()
    if uc.wait() != 0: raise IndexingFailureException(stderrdata)
    lynx = subprocess.Popen(["/usr/bin/lynx","-stdin","-dump","-width","1000"],shell=False,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    text, stderrdata = lynx.communicate(html)
    if lynx.wait() != 0: raise IndexingFailureException(stderrdata)
    return text

def ppthtml(os_pathname):
    ph = subprocess.Popen(["/usr/bin/ppthtml",os_pathname], shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    html, stderrdata = ph.communicate()
    if ph.wait() != 0: raise IndexingFailureException(stderrdata)
    elinks = subprocess.Popen(["/usr/bin/elinks","-dump","-dump-width","1000"],shell=False,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    text, stderrdata = elinks.communicate(html)
    if elinks.wait() != 0: raise IndexingFailureException(stderrdata)
    return text

def xlhtml(os_pathname):
    xh = subprocess.Popen(["/usr/bin/xlhtml",os_pathname], shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    html, stderrdata = xh.communicate()
    if xh.wait() != 0: raise IndexingFailureException(stderrdata)
    lynx = subprocess.Popen(["/usr/bin/lynx","-stdin","-dump","-width","1000"],shell=False,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    text, stderrdata = lynx.communicate(html)
    if lynx.wait() != 0: raise IndexingFailureException(stderrdata)
    return text

def wvhtml(os_pathname):
    wh = subprocess.Popen(["/usr/bin/wvWare", os_pathname], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    html, stderrdata = wh.communicate()
    if wh.wait() != 0: raise IndexingFailureException(stderrdata)
    elinks = subprocess.Popen(["/usr/bin/elinks","-dump","-dump-width","1000"],shell=False,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    text, stderrdata = elinks.communicate(html)
    if elinks.wait() != 0: raise IndexingFailureException(stderrdata)
    return text

def pdftotext(os_pathname):
    pt = subprocess.Popen(["/usr/bin/pdftotext",os_pathname, "-"], shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    text, stderrdata = pt.communicate()
    if pt.wait() != 0: raise IndexingFailureException(stderrdata)
    return nkf.nkf("-w", text)

def officexml(os_pathname):
    return officex.extract(os_pathname)

def extract(fullpath):
    extractor_funcs = {
        ".xls":xlhtml,
        ".xlsx":officexml,
        ".doc":wvhtml,
        ".docx":officexml,
        ".ppt":ppthtml,
        ".pptx":officexml,
        ".pdf":pdftotext
    }

    extractor_func = None
    for suffix, func in extractor_funcs.iteritems():
        if fullpath.lower().endswith(suffix):
            extractor_func = func
            break
    if extractor_func == None: raise IndexingFailureException("Unknown file type")
    return extractor_func(fullpath)

def run():
    shares = {}
    for share in oscar.get_share_list():
        shares[share[0]] = share

    queue = oscar.get("/indexing/")
    for indexing_target in queue:
        share_id = indexing_target[0]
        file_id = indexing_target[1]
        path = indexing_target[2]

        try:
            if share_id not in shares: raise IndexingFailureException("Share not found in smb.conf", share_id, file_id)
            base_dir = shares[share_id][1]
            fullpath = base_dir + path.encode("utf-8")
            print "Extracting %s..." % fullpath
            text = extract(fullpath)
            print oscar.post("/file/%s/%s/contents" % (share_id, file_id), text, "text/plain")
            oscar.delete("/indexing/%s/%s" % (share_id, file_id))
        except IndexingFailureException, e:
            print "%s:%s" % (share_id, file_id)
            print e.str
            print oscar.post("/indexing/%s/%s/fail" % (share_id,file_id), {})
        
if __name__ == '__main__':
    if len(sys.argv) < 2:
        with oscar.JobLock("indexing.lock") as l:
            if l: run()
    else:
        for file in sys.argv[1:]:
            print "Extracting %s..." % file
            print extract(file)
