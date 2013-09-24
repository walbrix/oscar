#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import os
import re
import subprocess
import hashlib
import urllib2
import argparse
import logging
import logging.handlers

import pyinotify

import oscar
import extract

__author__ = "Walbrix Corporation"
__version__ = "0.0.1"

class DoNothing():
    def __getattr__(self, name):
        def k(*a, **b):
            pass
        return k

log = DoNothing()

def logger_init(name, verbose=False, filename=None):
    """Initialize logger instance."""
    log = logging.getLogger(name)
    handler = logging.handlers.RotatingFileHandler(filename, 'a', 1024*1024*100,9) if filename else logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("[%(asctime)s %(name)s %(levelname)s] %(message)s"))
    log.addHandler(handler)
    log.setLevel(10 if verbose else 20)
    return log

def register_file(share_id, base_dir, filename):
    if os.path.islink(filename): return
    log.debug("register_file(%s,%s,%s)", share_id, base_dir, filename)
    if not os.path.isfile(filename): return
    os_pathname = os.path.realpath(filename)
    if not os_pathname.startswith(base_dir + '/'): return

    try:
        stat = os.stat(os_pathname)
    except OSError, e:
        # probably file doesn't exist
        log.error("File %s is not accessible(probably it doesn't exist). Ignoring register request." % os_pathname)
        return

    log.debug("stat=%s", str(stat))

    pathname = os_pathname[len(base_dir):]
    path, name = os.path.split(pathname)

    data = {"path":path,"name":name,"atime":int(stat.st_atime * 1000),"ctime":int(stat.st_ctime * 1000),"mtime":int(stat.st_mtime * 1000),"size":int(stat.st_size)}
    rst = oscar.post("/file/%s" % share_id, data)
    log.info("%s:%s registered. %s" % (share_id, filename, str(rst)))

    indexeable_suffixes = [".doc",".docx",".xls", ".xlsx", ".ppt", ".pptx", ".pdf", ".txt", ".html", ".htm", ".xhtml", ".csv"]
    if any(map(lambda x:pathname.lower().endswith(x), indexeable_suffixes)):
        rst = oscar.post("/indexing/%s" % share_id, {"path":pathname})
        log.info("%s:%s marked as indexeable. %s" % (share_id, pathname, str(rst)))

def request_perform_walk():
    oscar.request_perform_walk()
    log.info("Requested to perform full walk.")

def register_dir(share_id, base_dir, os_dirname):
    if not os_dirname.startswith(base_dir + '/'): return # it can't be but just for sure
    request_perform_walk()

def unregister_file(share_id, base_dir, filename):
    os_pathname = os.path.realpath(filename)
    if not os_pathname.startswith(base_dir + '/'): return
    pathname = os_pathname[len(base_dir):]

    file_id = hashlib.sha1(pathname).hexdigest()
    rst = oscar.delete("/file/%s/%s" % (share_id, file_id))
    log.info("%s:%s(%s) unregistered. %s" % (share_id, file_id, pathname, str(rst)))
    rst = oscar.delete("/indexing/%s/%s" % (share_id, file_id))
    if rst[0]:
        log.info("%s:%s(%s) unregistered from index queue. %s" % (share_id, file_id, pathname, str(rst)))

def unregister_dir(share_id, base_dir, os_pathname):
    if not os_pathname.startswith(base_dir + '/'): return
    pathname = os_pathname[len(base_dir):]
    #rst = oscar.delete("/file/%s" % share_id, {"path_prefix":pathname})
    #log.info("All files under %s:%s has been unregistered. %s" % (share_id, pathname, str(rst)))
    rst = oscar.delete("/indexing/%s" % share_id, {"path_prefix":pathname})
    log.info("All files under %s:%s has been unmarked as indexeable. %s" % (share_id, pathname, str(rst)))
    oscar.request_perform_cleanup()
    log.info("Requested to perform full cleanup.")

def process_dir(events, share_id, base_dir, full_path):
    if events & pyinotify.IN_MOVED_TO:
        log.debug("process_dir/MOVED_TO")
        register_dir(share_id, base_dir, full_path)
    elif events & pyinotify.IN_MOVED_FROM:
        log.debug("process_dir/MOVED_FROM")
        unregister_dir(share_id, base_dir, full_path)

def process_file(events, share_id, base_dir, full_path):
    if (events & pyinotify.IN_CLOSE_WRITE) or (events & pyinotify.IN_MOVED_TO):
        log.debug("process_file/IN_CLOSE_WRITE|IN_MOVED_TO")
        ignore_suffixes = [".tmp"]
        if not any(map(lambda x:full_path.lower().endswith(x), ignore_suffixes)):
            register_file(share_id, base_dir, full_path)
    elif (events & pyinotify.IN_DELETE) or (events & pyinotify.IN_MOVED_FROM):
        log.debug("process_file/IN_DELETE|IN_MOVED_FROM")
        unregister_file(share_id, base_dir, full_path)

def add(args):
    shares = oscar.get_share_list()
    for filename in args.args:
        for share in shares:
            share_id = share[0]
            base_dir = share[1]
            if not os.path.realpath(filename).startswith(base_dir + '/'): continue
            register_file(share_id, base_dir, filename)

def delete(args):
    shares = oscar.get_share_list()
    for filename in args.args:
        for share in shares:
            share_id = share[0]
            base_dir = share[1]
            if not os.path.realpath(filename).startswith(base_dir + '/'): continue
            unregister_file(share_id, base_dir, filename)

def watch(args):
    def callback(event):
        if not isinstance(event, pyinotify.Event): return
        log.debug(event)
        if event.mask & pyinotify.IN_IGNORED: return
        try:
            shares = oscar.get_share_list()
            for share in shares:
                share_id = share[0]
                base_dir = share[1]
                if not event.pathname.startswith(base_dir + '/'): continue
                if event.mask & pyinotify.IN_ISDIR:
                    log.debug("Process dir: %s" % event.pathname)
                    process_dir(event.mask, share_id, base_dir, event.pathname)
                else:
                    log.debug("Process file: %s" % event.pathname)
                    process_file(event.mask, share_id, base_dir, event.pathname)
        except urllib2.HTTPError, e:
            log.error(e.geturl())
            log.error(e.read())
        except Exception, e:
            log.exception("Got an exception")

    wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm, default_proc_fun=callback)
    mask = pyinotify.IN_CLOSE_WRITE|pyinotify.IN_MOVED_FROM|pyinotify.IN_MOVED_TO|pyinotify.IN_MOVED_TO|pyinotify.IN_CREATE|pyinotify.IN_DELETE
    wm.add_watch(map(lambda x:x[1], oscar.get_share_list()), mask, rec=True,auto_add=True)
        
    notifier.loop()

def walk(args):
    def process(share_id, base_dir, os_pathname):
        if not os_pathname.startswith(base_dir + '/'): return # it can't be but just for sure
        pathname = os_pathname[len(base_dir):]
        file_id = hashlib.sha1(pathname).hexdigest()
        exists = len(oscar.get("/file/%s" % share_id, {"file_id_prefix":file_id})) > 0
        if not exists:
            log.info("New file %s:%s(%s) discovered" % (share_id,file_id, os_pathname))
            register_file(share_id, base_dir, os_pathname)            

    with oscar.JobLock("walk.lock") as l:
        if not l: return # other index process has still been runnig
        oscar.remove_run_file("perform_walk")
        shares = oscar.get_share_list()
        for share in shares:
            share_id = share[0]
            base_dir = share[1]
            log.debug("Processing share [%s]" % share_id)
            for root, dirs, files in os.walk(share[1]):
                for file in files:
                    os_pathname = os.path.join(root, file)
                    process(share_id, base_dir, os_pathname)

def calcsum(args):
    def sha1sum(os_pathname):
        d = hashlib.sha1()
        try:
            with open(os_pathname) as f:
                while True:
                    x = f.read(1024*1024) # 1mb buf
                    if not x: break
                    d.update(x)
        except Exception, e:
            log.error("sha1sum calculation failed! %s" % str(e))
            return "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ"

        return d.hexdigest()

    with oscar.JobLock("calcsum.lock") as l:
        if not l: return
        shares = oscar.get_share_list()
        for share in shares:
            share_id = share[0]
            log.debug("Processing share [%s]" % share_id)
            base_dir = share[1]
            files_to_be_scanned = oscar.get("/file/%s/nosum" % share_id, {"limit":"5000"})
            for file in files_to_be_scanned:
                file_id, path, name = file[0], file[1], file[2]
                os_pathname = os.path.join(base_dir, re.sub(r'^/+','',path).encode("utf-8"), name.encode("utf-8"))
                if os.path.isfile(os_pathname):
                    rst = oscar.post("/file/%s/%s/sha1sum" % (share_id,file_id), {"sha1sum":sha1sum(os_pathname)})            
                    log.info("sha1sum calculation done for file %s:%s(%s,%s). %s" % (share_id,file_id, path, name, str(rst)))

def cleanup(args):
    with oscar.JobLock("cleanup.lock") as l:
        if not l: return # other index process has still been runnig

        oscar.remove_run_file("perform_cleanup")
        shares = oscar.get_share_list()
        for share in shares:
            share_id = share[0]
            log.debug("processing share [%s]" % share_id)
            base_dir = share[1]
            for segment in map(lambda x:"%02x" % x, range(0,256)):
                files_to_be_checked = oscar.get("/file/%s" % share_id, {"file_id_prefix":segment})
                log.debug("Processing segment %s (%d files)" % (segment, len(files_to_be_checked)))
                for file in files_to_be_checked:
                    file_id, path, name = file[0], file[1], file[2]
                    os_pathname = os.path.join(base_dir, re.sub(r'^/+','',path).encode("utf-8"), name.encode("utf-8"))
                    if not os.path.isfile(os_pathname):
                        unregister_file(share_id, base_dir, os_pathname)

def process_create_index(shares, share_id, file_id, path):
    try:
        if share_id not in shares:
            raise Exception("Share %s not found in smb.conf" % share_id)
        share = shares[share_id]
        base_dir = share[1]
        fullpath = base_dir + path.encode("utf-8")
        if not os.path.isfile(fullpath):
            raise Exception("File %s not found" % fullpath)
        log.debug("Extracting %s..." % fullpath.decode("utf-8"))
        text = extract.extract(fullpath)
        rst = oscar.post("/file/%s/%s/contents" % (share_id, file_id), text, "text/plain")
        log.info("%s:%s(%s) index commited. %s" % (share_id, file_id, path, str(rst)))
        rst = oscar.delete("/indexing/%s/%s" % (share_id, file_id))
        log.info("%s:%s(%s) marked as done. %s" % (share_id, file_id, path, str(rst)))
    except KeyboardInterrupt, e:
        raise e
    except Exception, e:
        log.error(e)
        rst = oscar.post("/indexing/%s/%s/fail" % (share_id,file_id), {})
        log.info("Indexing for %s:%s(%s) marked as fail: %s" % (share_id, file_id, path, str(rst)))

def create_index(args):
    with oscar.JobLock("indexing.lock") as l:
        if not l: return # other index process has still been runnig

        shares = {}
        for share in oscar.get_share_list():
            shares[share[0]] = share
        queue = oscar.get("/indexing/", {"limit":str(args.limit)})
        for indexing_target in queue:
            share_id = indexing_target[0]
            file_id = indexing_target[1]
            path = indexing_target[2]
            process_create_index(shares, share_id,file_id,path)

def reset_index(args):
    log.info("ATTEMPTING FULL RESET")
    rst = oscar.post("/admin/RESET", {})
    log.info("Full reset performed. Amen. %s" % str(rst))
    request_perform_walk()

def process_requested_jobs(args):
    # call flush api to cleanup mroonga
    rst = oscar.post("admin/FLUSH", {})
    log.debug("FLUSH TABLES performed. %s" % str(rst))

    log.debug("Checking perform_cleanup")
    if oscar.check_run_file("perform_cleanup"):
        log.info("Performing cleanup is requested.")
        cleanup(args)
    log.debug("Checking perform_walk")
    if oscar.check_run_file("perform_walk"):
        log.info("Performing full walk is requested.")
        walk(args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-l", "--log", default=None)

    subparsers = parser.add_subparsers()

    parser_add = subparsers.add_parser("add")
    parser_add.add_argument("args", nargs='*')
    parser_add.set_defaults(func=add)

    parser_delete = subparsers.add_parser("delete")
    parser_delete.add_argument("args", nargs='*')
    parser_delete.set_defaults(func=delete)

    parser_watch = subparsers.add_parser("watch")
    parser_watch.set_defaults(func=watch)

    parser_walk = subparsers.add_parser("walk")
    parser_walk.set_defaults(func=walk)

    parser_calcsum = subparsers.add_parser("calcsum")
    parser_calcsum.set_defaults(func=calcsum)

    parser_cleanup = subparsers.add_parser("cleanup")
    parser_cleanup.set_defaults(func=cleanup)

    parser_create_index = subparsers.add_parser("create_index")
    parser_create_index.add_argument("--limit", default=5000)
    parser_create_index.set_defaults(func=create_index)

    parser_reset_index = subparsers.add_parser("reset_index")
    parser_reset_index.set_defaults(func=reset_index)

    parser_process_requested_jobs = subparsers.add_parser("process_requested_jobs")
    parser_process_requested_jobs.set_defaults(func=process_requested_jobs)


    args = parser.parse_args()

    log = logger_init("oscar", args.verbose, args.log)

    try:
        args.func(args)
    except urllib2.HTTPError, e:
        log.error(e.read())
        log.exception('Got an HTTP Error')
        raise
    except:
        log.exception("Got an exception")
        raise
