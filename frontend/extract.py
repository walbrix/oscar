#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import sys
import os
import re
import subprocess
import nkf
import oscar
import officex

class IndexingFailureException(Exception):
    def __init__(self, str):
        self.str = str
    def __str__(self):
        return u"Indexing failure '%s'" % (self.str)

def process_output(cmdline, timeout=30):
    proc = subprocess.Popen(["/usr/bin/timeout",str(timeout)] + cmdline, shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    stdoutdata, stderrdata = proc.communicate()
    rst = proc.wait()
    if rst == 124:
        raise IndexingFailureException("Process Timeout (%dsec)" % timeout)
    elif rst != 0:
        raise IndexingFailureException(stderrdata)
    return stdoutdata

def elinks(html):
    my_env = os.environ.copy()
    my_env["LANG"] = "ja_JP.utf8"
    elinks = subprocess.Popen(["/usr/bin/elinks","-dump","-dump-width","1000","-dump-charset","utf-8"],shell=False,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=my_env)
    text, stderrdata = elinks.communicate(html)
    if elinks.wait() != 0: raise IndexingFailureException(stderrdata)
    return text

def unoconv(os_pathname):
    html = process_output(["/usr/bin/unoconv","-f","html","--stdout",os_pathname], 30)
    lynx = subprocess.Popen(["/usr/bin/lynx","-stdin","-dump","-width","1000"],shell=False,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    text, stderrdata = lynx.communicate(html)
    if lynx.wait() != 0: raise IndexingFailureException(stderrdata)
    return text

def ppthtml(os_pathname):
    html = process_output(["/usr/bin/ppthtml",os_pathname])
    text = elinks(html)
    text = re.sub(ur'[ 　]+', ' ', text.decode("utf-8"))
    text = re.sub(ur'_+', '_', text)
    text = re.sub(ur'-+', '-', text)
    return text.encode("utf-8")

def xlhtml(os_pathname):
    html = process_output(["/usr/bin/xlhtml",os_pathname])
    lynx = subprocess.Popen(["/usr/bin/lynx","-stdin","-dump","-width","1000"],shell=False,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    text, stderrdata = lynx.communicate(html)
    if lynx.wait() != 0: raise IndexingFailureException(stderrdata)
    text = re.sub(ur'[ 　]+', ' ', text.decode("utf-8"))
    text = re.sub(ur'_+', '_', text)
    text = re.sub(ur'-+', '-', text)
    return text.encode("utf-8")

def xlhtml(os_pathname):
    html = process_output(["/usr/bin/xlhtml",os_pathname])
    lynx = subprocess.Popen(["/usr/bin/lynx","-stdin","-dump","-width","1000"],shell=False,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    text, stderrdata = lynx.communicate(html)
    if lynx.wait() != 0: raise IndexingFailureException(stderrdata)
    text = re.sub(ur'[ 　]+', ' ', text.decode("utf-8"))
    return text.encode("utf-8")

def wvhtml(os_pathname):
    html = process_output(["/usr/bin/wvWare", "--nographics", os_pathname])
    text = elinks(html)
    text = re.sub(ur'[ 　]+', ' ', text.decode("utf-8"))
    text = re.sub(ur'-+', '-', text)
    return text.encode("utf-8")

def pdftotext(os_pathname):
    text = process_output(["/usr/bin/pdftotext",os_pathname, "-"])
    return nkf.nkf("-w", text)

def text(os_pathname):
    text = open(os_pathname).read()
    return nkf.nkf("-w", text)

def htmltotext(os_pathname):
    html = open(os_pathname).read()
    html = nkf.nkf("-w", html)
    elinks = subprocess.Popen(["/usr/bin/elinks","-dump","-dump-width","1000"],shell=False,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    text, stderrdata = elinks.communicate(html)
    if elinks.wait() != 0: raise IndexingFailureException(stderrdata)
    return text

def officexml(os_pathname):
    text = officex.extract(os_pathname)
    if not text: raise IndexingFailureException("Empty document")
    return text

def extract(fullpath):
    extractor_funcs = {
        ".xls":xlhtml,
        ".xlsx":officexml,
        ".doc":wvhtml,
        ".docx":officexml,
        ".ppt":ppthtml,
        ".pptx":officexml,
        ".pdf":pdftotext,
        ".txt":text,
        ".csv":text,
        ".tsv":text,
        ".htm":htmltotext,
        ".html":htmltotext
    }

    extractor_func = None
    for suffix, func in extractor_funcs.iteritems():
        if fullpath.lower().endswith(suffix):
            extractor_func = func
            break
    if extractor_func == None: raise IndexingFailureException("Unknown file type")
    return extractor_func(fullpath)
        
if __name__ == '__main__':
    for file in sys.argv[1:]:
        print "Extracting %s..." % file
        print extract(file)
