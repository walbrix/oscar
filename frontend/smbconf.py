#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import ConfigParser
import re
import urllib2

smb_conf = "/etc/samba/smb.conf"

_smbconf_timestamp = None
_smbconf = None

def _get_parser():
    timestamp = os.stat(smb_conf).st_mtime
    global _smbconf, _smbconf_timestamp
    if not _smbconf or not _smbconf_timestamp or _smbconf_timestamp < timestamp:
        _smbconf = ConfigParser.SafeConfigParser({"guest ok":"no","writable":"no","locking":"yes","valid users":None})
        _smbconf.read(smb_conf)
        _smbconf_timestamp = timestamp
    return _smbconf

def get(section, option):
    return _get_parser().get(section, option)

def sections():
    return _get_parser().sections()

class Share:
    def __init__(self, name, path, guest_ok=False, writable=False, comment=None,locking=True,valid_users=None):
        self.name = name if isinstance(name, unicode) else name.decode("utf-8")
        self.path = path
        self.guest_ok = guest_ok
        self.writable = writable
        self.comment = comment if isinstance(comment, unicode) else comment.decode("utf-8")
        self.locking = locking
        self.valid_users = valid_users

    def real_path(self, path):
        if isinstance(path, unicode): path = path.encode("utf-8")
        if path.startswith('/'): path = re.sub(r'^/+', "", path)
        return os.path.join(self.path, path)

    def urlencoded_name(self):
        return urllib2.quote(self.name.encode("utf-8"))

    def is_user_valid(self, user, groups):
        if self.valid_users == None: return True
        valid_users = map(lambda x:x.lower(), self.valid_users.split())
        if user.lower() in valid_users: return True
        for group in groups:
            if '@' + group.lower() in valid_users: return True
        return False

class NoSuchShareException(Exception):
    def __init__(self, name):
        Exception.__init__(self, name)

_ignoreable_sections = ["static","global","homes","printers"]

def shares():
    share_list = []
    parser = _get_parser()
    for section in filter(lambda x:x not in _ignoreable_sections, sections()):
        share = get_share(section, parser)
        if share.locking:  # ignore locking = no shares
            share_list.append(share)
    return share_list

def share_exists(name):
    return name not in _ignoreable_sections and _get_parser().has_section(name)

def get_share(name, parser=None):
    if isinstance(name, unicode): name = name.encode("utf-8")
    if not parser: parser = _get_parser()
    if name in _ignoreable_sections or not parser.has_section(name):
        raise NoSuchShareException(name)
    path = parser.get(name, "path")
    guest_ok = parser.getboolean(name, "guest ok")
    writable = parser.getboolean(name, "writable")
    comment = parser.get(name, "comment") if parser.has_option(name, "comment") else (u"共有フォルダ" if guest_ok else u"アクセス制限された共有フォルダ")
    locking = parser.getboolean(name, "locking")
    valid_users = parser.get(name, "valid users")
    return Share(name, path, guest_ok=guest_ok, writable=writable, comment=comment,locking=locking,valid_users=valid_users)

if __name__ == "__main__":
    for share in shares():
        print share.name.encode("utf-8")
        print share.comment.encode("utf-8")
        print share.valid_users

    print get_share(u"しぇあー").urlencoded_name()
    print get_share(u"ないしぇあー")
