#!/usr/bin/python2.7
import os
import re
import subprocess
import hashlib
import argparse
import oscar

def register_file(filename):
    if os.path.islink(filename): return
    if not os.path.isfile(filename): return
    os_pathname = os.path.realpath(filename)
    if not os_pathname.startswith(oscar.base_dir + '/'): return

    stat = os.stat(os_pathname)

    pathname = os_pathname[len(oscar.base_dir):]
    path, name = os.path.split(pathname)

    data = {"path":path,"name":name,"atime":int(stat.st_atime * 1000),"ctime":int(stat.st_ctime * 1000),"mtime":int(stat.st_mtime * 1000),"size":int(stat.st_size)}
    print oscar.post("/file/", data)

    indexeable_suffixes = [".doc",".docx",".xls", ".xlsx", ".ppt", ".pptx", ".pdf", ".txt", ".html", ".htm", ".xhtml"]
    if any(map(lambda x:pathname.lower().endswith(x), indexeable_suffixes)):
        print oscar.post("/indexing/", {"path":pathname})

def register_dir(dirname):
    pass

def unregister_file(filename):
    os_pathname = os.path.realpath(filename)
    if not os_pathname.startswith(oscar.base_dir + '/'): return
    pathname = os_pathname[len(oscar.base_dir):]

    print oscar.delete("/file/%s" % hashlib.sha1(pathname).hexdigest())
    print oscar.delete("/indexing/%s" % hashlib.sha1(pathname).hexdigest())

def unregister_dir(dirname):
    pass

def add(args):
    for filename in args.args:
        register_file(filename)

def delete(args):
    for filename in args.args:
        unregister_file(filename)

def process_dir(events, full_path):
    if "MOVED_TO" in events: register_dir(full_path)
    elif "MOVED_FROM" in events: unregister_dir(full_path)

def process_file(events, full_path):
    if "CLOSE_WRITE" in events or "MOVED_TO" in events:
        register_file(full_path)
    elif "DELETE" in events or "MOVED_FROM" in events:
        unregister_file(full_path)

def process_inotifywait_line(line):
    pat = re.compile(r"^(.*?\/) (.*?) (.*)$")
    match = pat.match(line)
    if not match: return
    groups = match.groups()
    if len(groups) != 3: return
    directory, event, content = match.groups()
    if not directory.startswith(oscar.base_dir + '/'): return
    full_path = directory + content

    events = event.split(',')
    if "ISDIR" in events: process_dir(events, full_path)
    else: process_file(events, full_path)

def watch(args):
    inotifywait = subprocess.Popen(["/usr/bin/inotifywait", "-m", "-r", oscar.base_dir], shell=False, stdout=subprocess.PIPE)
    line = inotifywait.stdout.readline()
    while line:
        process_inotifywait_line(line.strip())
        line = inotifywait.stdout.readline()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    parser_add = subparsers.add_parser("add")
    parser_add.add_argument("args", nargs='*')
    parser_add.set_defaults(func=add)

    parser_delete = subparsers.add_parser("delete")
    parser_delete.add_argument("args", nargs='*')
    parser_delete.set_defaults(func=delete)

    parser_watch = subparsers.add_parser("watch")
    parser_watch.set_defaults(func=watch)

    args = parser.parse_args()

    args.func(args)

